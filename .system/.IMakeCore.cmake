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

    file(TO_CMAKE_PATH "$ENV{IMAKECORE_ROOT}/.system/IMakeCore.py" script_path)
    execute_process(
        COMMAND  ${Python_EXECUTABLE} -B ${script_path} ${CMAKE_CURRENT_LIST_DIR} cmake
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
    if(NOT DEFINED IMAKECORE_ROOT_DIR)
        set(IMAKECORE_ROOT_DIR "${CMAKE_SOURCE_DIR}")
    endif()
    foreach(target $CACHE{TARGET_CACHE})
        set(IMAKECORE_TARGET ${target})
        include(${IMAKECORE_ROOT_DIR}/.package.cmake)
    endforeach()

endfunction()

function(initializeTarget)
    list(LENGTH ARGN argc)
    if(argc EQUAL 0)
        message(FATAL_ERROR "initializeTarget function must contains at least one target name")
    endif()
    set(TARGET_CACHE ${ARGN} CACHE INTERNAL "" FORCE)

    resolvePackageInfo()
endfunction()

function(ICmakeCoreInit)
    initializeTarget(${ARGV})
endfunction()


