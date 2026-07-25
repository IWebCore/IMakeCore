cmake_minimum_required(VERSION 3.16)
project(project_resolve_pch LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 17)

add_executable(project_resolve_pch main.cpp)

# --- IMakeCore integration ---
set(SYS_IMR "$ENV{IMAKECORE_ROOT}")
get_filename_component(TEST_ROOT "${CMAKE_CURRENT_SOURCE_DIR}/../" ABSOLUTE)
set(ENV{IMAKECORE_ROOT} "${TEST_ROOT}")
set(ENV{IMAKECORE_SYSTEM} "${SYS_IMR}/.system")
include($ENV{ICMakeCore})
ICmakeCoreInit(project_resolve_pch)
