cmake_minimum_required(VERSION 3.16)
project(project_static LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 17)

# Test environment
set(ENV{IMAKECORE_ROOT} "C:/Users/Yue/IMakeCore/test/static_propagation")
set(ENV{IMAKECORE_SYSTEM} "C:/Users/Yue/IMakeCore/.system")

include($ENV{ICMakeCore})
ICmakeCoreInit(project_static)
include(${CMAKE_CURRENT_SOURCE_DIR}/.package.cmake)

add_executable(project_static main.cpp)
