# test@world@1.0.0 — DO NOT EDIT
cmake_minimum_required(VERSION 3.16)
project(test_world_1_0_0 LANGUAGES CXX)

add_library(test_world_1_0_0 STATIC)
set_target_properties(test_world_1_0_0 PROPERTIES LINKER_LANGUAGE CXX)
set_target_properties(test_world_1_0_0 PROPERTIES
    ARCHIVE_OUTPUT_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/${CMAKE_SYSTEM_PROCESSOR}-${CMAKE_SYSTEM_NAME}-static"
)

set(IMAKECORE_ROOT_DIR "${CMAKE_CURRENT_SOURCE_DIR}")
include($ENV{ICMakeCore})
ICmakeCoreInit(test_world_1_0_0)
