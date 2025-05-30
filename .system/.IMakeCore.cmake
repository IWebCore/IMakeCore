function(cacheTo)
    list(POP_FRONT ARGN cache_var_name)
    list(JOIN ARGN ";" cached_list_value)
    list(APPEND cached_list_value  $CACHE{${cache_var_name}})
    set(${cache_var_name} ${cached_list_value} CACHE INTERNAL "" FORCE)
endfunction()

function(cacheToSources)
    cacheTo(SOURCES_CACHE ${ARGV})
endfunction()

function(cacheToHeaders)
    cacheTo(HEADERS_CACHE ${ARGV})
endfunction()

function(cacheToIncludes)
    cacheTo(INCLUDES_CACHE ${ARGV})
endfunction(cacheToIncludes)

function(cacheToResources)
    cacheTo(SOURCES_CACHE ${ARGV})
endfunction()

function(cacheToLibraries)
    cacheTo(LIBRARIES_CACHE ${ARGV})
endfunction()

function(cacheToDefinitions)
    cacheTo(DEFINITIONS_CACHE ${ARGV})
endfunction()

function(prepareCacheVariables)
    set(HEADERS_CACHE CACHE INTERNAL "" FORCE)
    set(SOURCES_CACHE CACHE INTERNAL "" FORCE)
    set(INCLUDES_CACHE CACHE INTERNAL "" FORCE)
    set(LIBRARIES_CACHE CACHE INTERNAL "" FORCE)
    set(DEFINITIONS_CACHE CACHE INTERNAL "" FORCE)
endfunction()

function(resolvePackageInfo)
    find_program(Python_EXECUTABLE python) 
    if("${Python_EXECUTABLE}" STREQUAL "")
        message(FATAL_ERROR "Python not found")
        return()
    endif()

    file(TO_CMAKE_PATH "$ENV{IMAKECORE_ROOT}/.system/IMakeCore.py" script_path)
    execute_process(
        COMMAND  ${Python_EXECUTABLE} ${script_path} ${CMAKE_CURRENT_LIST_DIR} cmake
        OUTPUT_VARIABLE infoVal
        RESULT_VARIABLE result
        # COMMAND_ECHO STDOUT
    )

    if (NOT infoVal STREQUAL "")
        message(STATUS "${infoVal}")
    endif()
    
    if (NOT result EQUAL 0)
        message(FATAL_ERROR "packages configuration failed")
        return()
    endif()
    
    message(STATUS "packages configured successfully")
    include(${CMAKE_SOURCE_DIR}/.package.cmake)

endfunction()

function(assambleTarget)
    foreach(target $CACHE{TARGET_CACHE})
        target_sources(${target} PRIVATE ${SOURCES_CACHE} ${HEADERS_CACHE})
        target_include_directories(${target} PRIVATE $CACHE{INCLUDES_CACHE})
        target_link_libraries(${target} PRIVATE $CACHE{LIBRARY_CACHE})
        target_compile_definitions(${target} PRIVATE $CACHE{DEFINITIONS_CACHE})
    endforeach()
endfunction()

function(initializeTarget)
    list(LENGTH ARGN argc)
    if(argc EQUAL 0)
        message(FATAL_ERROR "initializeTarget function must contains at least one target name")
    endif()
    set(TARGET_CACHE ${ARGN} CACHE INTERNAL "" FORCE)

    prepareCacheVariables()
    resolvePackageInfo()
    assambleTarget()
endfunction()

function(ICmakeCoreInit)
    initializeTarget(${ARGV})
endfunction()