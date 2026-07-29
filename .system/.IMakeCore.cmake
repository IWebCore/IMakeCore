# ── Helper: get executable output directory ────────────────────────
function(getExecutablePath OUT_VAR)
    if(DEFINED CMAKE_RUNTIME_OUTPUT_DIRECTORY)
        set(${OUT_VAR} "${CMAKE_RUNTIME_OUTPUT_DIRECTORY}" PARENT_SCOPE)
    else()
        set(${OUT_VAR} "${CMAKE_CURRENT_BINARY_DIR}" PARENT_SCOPE)
    endif()
endfunction()

# ── Helper: get target type ────────────────────────────────────────
function(getTargetType TARGET_NAME OUT_VAR)
    get_property(target_type TARGET ${TARGET_NAME} PROPERTY TYPE)
    if(target_type STREQUAL "STATIC_LIBRARY")
        set(${OUT_VAR} "static" PARENT_SCOPE)
    elseif(target_type STREQUAL "SHARED_LIBRARY" OR target_type STREQUAL "MODULE_LIBRARY")
        set(${OUT_VAR} "dynamic" PARENT_SCOPE)
    else()
        set(${OUT_VAR} "executable" PARENT_SCOPE)
    endif()
endfunction()

# ── Helper: get compile arguments ───────────────────────────────────
function(getCompileArguments)
    # platform
    if(WIN32)
        set(PLATFORM "windows")
    elseif(APPLE)
        set(PLATFORM "macos")
    elseif(UNIX)
        set(PLATFORM "linux")
    else()
        set(PLATFORM "unknown")
    endif()
    set(ENV{IMAKECORE_PLATFORM} "${PLATFORM}")

    # arch
    if(CMAKE_SIZEOF_VOID_P EQUAL 8)
        set(ARCH "x86_64")
    else()
        set(ARCH "x86")
    endif()
    set(ENV{IMAKECORE_ARCH} "${ARCH}")

    # compiler
    if(MSVC)
        set(COMPILER "msvc")
    elseif(CMAKE_CXX_COMPILER_ID STREQUAL "GNU")
        set(COMPILER "gcc")
    elseif(CMAKE_CXX_COMPILER_ID MATCHES "Clang")
        set(COMPILER "clang")
    else()
        set(COMPILER "${CMAKE_CXX_COMPILER_ID}")
    endif()
    set(ENV{IMAKECORE_COMPILER} "${COMPILER}")

    # compiler version
    set(ENV{IMAKECORE_COMPILER_VERSION} "${CMAKE_CXX_COMPILER_VERSION}")

    # build mode
    set(ENV{IMAKECORE_BUILD_MODE} "$<IF:$<CONFIG:Debug>,debug,release>")
    # Fallback if generator expression not available
    if(CMAKE_BUILD_TYPE)
        string(TOLOWER "${CMAKE_BUILD_TYPE}" mode_lower)
        set(ENV{IMAKECORE_BUILD_MODE} "${mode_lower}")
    endif()

    # runtimes
    if(MSVC)
        if(CMAKE_MSVC_RUNTIME_LIBRARY MATCHES "DLL")
            set(RT "dynamic")
        else()
            set(RT "static")
        endif()
    else()
        set(RT "system")
    endif()
    set(ENV{IMAKECORE_RUNTIMES} "${RT}")

    # c++ standard
    set(ENV{IMAKECORE_CPP_STD} "${CMAKE_CXX_STANDARD}")

    # exceptions
    if(CMAKE_CXX_FLAGS MATCHES "-fno-exceptions" OR CMAKE_CXX_FLAGS MATCHES "/EHsc-")
        set(ENV{IMAKECORE_EXCEPTION_ENABLED} "0")
    else()
        set(ENV{IMAKECORE_EXCEPTION_ENABLED} "1")
    endif()

    # rtti
    if(CMAKE_CXX_FLAGS MATCHES "-fno-rtti" OR CMAKE_CXX_FLAGS MATCHES "/GR-")
        set(ENV{IMAKECORE_RTTI_ENABLED} "0")
    else()
        set(ENV{IMAKECORE_RTTI_ENABLED} "1")
    endif()
endfunction()


# ── Main resolution function ──────────────────────────────────────
function(resolvePackageInfo)
    if(WIN32)
        find_program(Python_EXECUTABLE python)
    else()
        find_package(Python 3 REQUIRED COMPONENTS Interpreter)
    endif()

    if("${Python_EXECUTABLE}" STREQUAL "")
        message(FATAL_ERROR "Python not found")
        return()
    endif()

    if(NOT DEFINED CACHE{IMAKECORE_ROOT})
        set(IMAKECORE_ROOT "$ENV{IMAKECORE_ROOT}" CACHE STRING "root" FORCE)
    endif()
    if(NOT DEFINED CACHE{IMAKECORE_SYSTEM})
        set(IMAKECORE_SYSTEM "$ENV{IMAKECORE_ROOT}/.system" CACHE STRING "system" FORCE)
    endif()

    # Gather compile info (use first target)
    list(GET TARGET_CACHE 0 FIRST_TARGET)
    getExecutablePath(EXE_PATH)
    getTargetType(${FIRST_TARGET} TARGET_TYPE)
    getCompileArguments()

    set(ENV{IMAKECORE_EXECUTABLE_PATH} "${EXE_PATH}")
    set(ENV{IMAKECORE_TARGET_TYPE} "${TARGET_TYPE}")

    file(TO_CMAKE_PATH "$CACHE{IMAKECORE_SYSTEM}/IMakeCore.py" script_path)
    execute_process(
        COMMAND ${CMAKE_COMMAND} -E env
            "IMAKECORE_ROOT=$CACHE{IMAKECORE_ROOT}"
            "IMAKECORE_SYSTEM=$CACHE{IMAKECORE_SYSTEM}"
            "IMAKECORE_EXECUTABLE_PATH=$ENV{IMAKECORE_EXECUTABLE_PATH}"
            "IMAKECORE_TARGET_TYPE=$ENV{IMAKECORE_TARGET_TYPE}"
            "IMAKECORE_PLATFORM=$ENV{IMAKECORE_PLATFORM}"
            "IMAKECORE_ARCH=$ENV{IMAKECORE_ARCH}"
            "IMAKECORE_COMPILER=$ENV{IMAKECORE_COMPILER}"
            "IMAKECORE_COMPILER_VERSION=$ENV{IMAKECORE_COMPILER_VERSION}"
            "IMAKECORE_BUILD_MODE=$ENV{IMAKECORE_BUILD_MODE}"
            "IMAKECORE_RUNTIMES=$ENV{IMAKECORE_RUNTIMES}"
            "IMAKECORE_CPP_STD=$ENV{IMAKECORE_CPP_STD}"
            "IMAKECORE_EXCEPTION_ENABLED=$ENV{IMAKECORE_EXCEPTION_ENABLED}"
            "IMAKECORE_RTTI_ENABLED=$ENV{IMAKECORE_RTTI_ENABLED}"
            ${Python_EXECUTABLE} -B ${script_path} ${CMAKE_CURRENT_LIST_DIR} cmake
        OUTPUT_VARIABLE infoVal
        RESULT_VARIABLE result
    )

    if (NOT infoVal STREQUAL "")
        message(STATUS "${infoVal}")
    endif()
    if (NOT result EQUAL 0)
        message(FATAL_ERROR "packages configuration failed")
        return()
    endif()
    message(STATUS "packages configured successfully")
    foreach(target ${TARGET_CACHE})
        set(IMAKECORE_TARGET ${target})
        include(${CMAKE_CURRENT_LIST_DIR}/.package.cmake)
    endforeach()
endfunction()

function(initializeTarget)
    if(${ARGC} EQUAL 0)
        message(FATAL_ERROR "initializeTarget must have at least one target name")
    endif()
    set(TARGET_CACHE ${ARGV} CACHE INTERNAL "" FORCE)
    resolvePackageInfo()
endfunction()

function(ICmakeCoreInit)
    initializeTarget(${ARGV})
endfunction()
