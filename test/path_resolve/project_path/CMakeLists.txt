cmake_minimum_required(VERSION 3.16)
project(project_path LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 17)

add_executable(project_path main.cpp)

# --- IMakeCore integration ---
get_filename_component(TEST_ROOT "${CMAKE_CURRENT_SOURCE_DIR}/../" ABSOLUTE)
set(IMAKECORE_ROOT "${TEST_ROOT}" CACHE STRING "root" FORCE)
set(IMAKECORE_SYSTEM "$ENV{IMAKECORE_ROOT}/.system" CACHE STRING "system" FORCE)
include($ENV{ICMakeCore})
ICmakeCoreInit(project_path)
