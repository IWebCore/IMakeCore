# test@hello@2.0.0 — DO NOT EDIT
cmake_minimum_required(VERSION 3.16)
project(test_hello_2_0_0 LANGUAGES CXX)

add_library(test_hello_2_0_0 STATIC)
set_target_properties(test_hello_2_0_0 PROPERTIES LINKER_LANGUAGE CXX)
set_target_properties(test_hello_2_0_0 PROPERTIES
    ARCHIVE_OUTPUT_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/${CMAKE_SYSTEM_PROCESSOR}-${CMAKE_SYSTEM_NAME}-static"
)

set(IMAKECORE_ROOT_DIR "${CMAKE_CURRENT_SOURCE_DIR}")
include($ENV{ICMakeCore})
ICmakeCoreInit(test_hello_2_0_0)
