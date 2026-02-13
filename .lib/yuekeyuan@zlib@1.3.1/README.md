# NOTE

for details, please refer to [README](./README)

if you compile it with cmake, in your cmake file, add the following code:

```cmakelists
cmake_minimum_required(VERSION 3.20)
project(untitled LANGUAGES C CXX)

set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -std=c11")
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

```

noticed that in project command, we set the language to C and CXX, and set the standard to c11 and c++17. you must add C language support to your project to use this library.
