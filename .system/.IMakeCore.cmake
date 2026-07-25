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

    # message(STATUS ------ $ENV{IMAKECORE_ROOT})

    file(TO_CMAKE_PATH "$CACHE{IMAKECORE_SYSTEM}/IMakeCore.py" script_path)
    execute_process(
        COMMAND ${CMAKE_COMMAND} -E env
            "IMAKECORE_ROOT=$CACHE{IMAKECORE_ROOT}"
            "IMAKECORE_SYSTEM=$CACHE{IMAKECORE_SYSTEM}"
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
