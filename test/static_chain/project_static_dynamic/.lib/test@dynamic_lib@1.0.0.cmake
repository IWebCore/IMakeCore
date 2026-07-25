# SYSTEM AUTO GENERATED DO NOT EDIT!!!
# test@dynamic_lib@1.0.0
# Test dynamic library

set(current_lib_path "C:/Users/Yue/IMakeCore/test/static_chain/.lib/test@dynamic_lib@1.0.0")

target_include_directories(${IMAKECORE_TARGET} PRIVATE
    "${current_lib_path}"
)

target_sources(${IMAKECORE_TARGET} PRIVATE
    "${current_lib_path}/lib.h"
)

target_compile_definitions(${IMAKECORE_TARGET} PRIVATE sources)
target_compile_definitions(${IMAKECORE_TARGET} PRIVATE headers)

if(MSVC)
    target_link_libraries(${IMAKECORE_TARGET} PRIVATE "${CMAKE_CURRENT_LIST_DIR}/../.support/test@dynamic_lib@1.0.0_dynamic/${CMAKE_SYSTEM_PROCESSOR}-${CMAKE_SYSTEM_NAME}-dynamic/test_dynamic_lib_1_0_0.lib")
elseif(MINGW)
    target_link_libraries(${IMAKECORE_TARGET} PRIVATE "${CMAKE_CURRENT_LIST_DIR}/../.support/test@dynamic_lib@1.0.0_dynamic/${CMAKE_SYSTEM_PROCESSOR}-${CMAKE_SYSTEM_NAME}-dynamic/libtest_dynamic_lib_1_0_0.a")
elseif(APPLE)
    target_link_libraries(${IMAKECORE_TARGET} PRIVATE "${CMAKE_CURRENT_LIST_DIR}/../.support/test@dynamic_lib@1.0.0_dynamic/${CMAKE_SYSTEM_PROCESSOR}-${CMAKE_SYSTEM_NAME}-dynamic/libtest_dynamic_lib_1_0_0.dylib")
else()
    target_link_libraries(${IMAKECORE_TARGET} PRIVATE "${CMAKE_CURRENT_LIST_DIR}/../.support/test@dynamic_lib@1.0.0_dynamic/${CMAKE_SYSTEM_PROCESSOR}-${CMAKE_SYSTEM_NAME}-dynamic/libtest_dynamic_lib_1_0_0.so")
endif()

