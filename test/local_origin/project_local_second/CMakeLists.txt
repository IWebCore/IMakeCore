cmake_minimum_required(VERSION 3.16)
project(project_local_second LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 17)

add_executable(project_local_second main.cpp)

# --- IMakeCore integration (env vars + include at bottom) ---
get_filename_component(TEST_ROOT "${CMAKE_CURRENT_SOURCE_DIR}/../.." ABSOLUTE)
get_filename_component(SYSTEM_DIR "${CMAKE_CURRENT_SOURCE_DIR}/../../../.system" ABSOLUTE)
set(ENV{IMAKECORE_ROOT} "${TEST_ROOT}")
set(ENV{IMAKECORE_SYSTEM} "${SYSTEM_DIR}")
include($ENV{ICMakeCore})
ICmakeCoreInit(project_local_second)
include(${CMAKE_CURRENT_SOURCE_DIR}/.package.cmake)
