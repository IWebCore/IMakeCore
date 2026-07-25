# test@dynamic_lib@1.0.0 — DO NOT EDIT
cmake_minimum_required(VERSION 3.16)
project(test_dynamic_lib_1_0_0 LANGUAGES CXX)

add_library(test_dynamic_lib_1_0_0 SHARED)
set_target_properties(test_dynamic_lib_1_0_0 PROPERTIES LINKER_LANGUAGE CXX)
set_target_properties(test_dynamic_lib_1_0_0 PROPERTIES
    ARCHIVE_OUTPUT_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/${CMAKE_SYSTEM_PROCESSOR}-${CMAKE_SYSTEM_NAME}-dynamic"
    LIBRARY_OUTPUT_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/${CMAKE_SYSTEM_PROCESSOR}-${CMAKE_SYSTEM_NAME}-dynamic"
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/${CMAKE_SYSTEM_PROCESSOR}-${CMAKE_SYSTEM_NAME}-dynamic"
)

target_compile_definitions(test_dynamic_lib_1_0_0 PRIVATE sources)
target_compile_definitions(test_dynamic_lib_1_0_0 PRIVATE headers)

set(IMAKECORE_ROOT_DIR "${CMAKE_CURRENT_SOURCE_DIR}")
include($ENV{ICMakeCore})
ICmakeCoreInit(test_dynamic_lib_1_0_0)

add_custom_command(TARGET test_dynamic_lib_1_0_0 POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E make_directory "${CMAKE_CURRENT_SOURCE_DIR}/../../.bin"
    COMMAND ${CMAKE_COMMAND} -E copy_if_different "$<TARGET_FILE:test_dynamic_lib_1_0_0>" "${CMAKE_CURRENT_SOURCE_DIR}/../../.bin/"
)
