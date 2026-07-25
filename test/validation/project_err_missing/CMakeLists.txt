cmake_minimum_required(VERSION 3.16)
project(project_err_missing LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 17)

# Test environment (relative paths — portable across machines)
get_filename_component(TEST_ROOT "${CMAKE_CURRENT_SOURCE_DIR}/../.." ABSOLUTE)
get_filename_component(SYSTEM_DIR "${CMAKE_CURRENT_SOURCE_DIR}/../../../.system" ABSOLUTE)
set(ENV{IMAKECORE_ROOT} "${TEST_ROOT}")
set(ENV{IMAKECORE_SYSTEM} "${SYSTEM_DIR}")

include($ENV{ICMakeCore})
ICmakeCoreInit(project_err_missing)
include(${CMAKE_CURRENT_SOURCE_DIR}/.package.cmake)

add_executable(project_err_missing main.cpp)
