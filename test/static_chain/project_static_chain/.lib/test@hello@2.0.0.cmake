# SYSTEM AUTO GENERATED DO NOT EDIT!!!
# test@hello@2.0.0
# Test source library v2 (contains .cpp)

set(current_lib_path "C:/Users/Yue/IMakeCore/test/static_chain/.lib/test@hello@2.0.0")

target_include_directories(${IMAKECORE_TARGET} PRIVATE
    "${current_lib_path}"
)

target_sources(${IMAKECORE_TARGET} PRIVATE
    "${current_lib_path}/hello.h"
)

if(MSVC)
    target_link_libraries(${IMAKECORE_TARGET} PRIVATE "${CMAKE_CURRENT_LIST_DIR}/../.support/test@hello@2.0.0_static/${CMAKE_SYSTEM_PROCESSOR}-${CMAKE_SYSTEM_NAME}-static/test_hello_2_0_0.lib")
else()
    target_link_libraries(${IMAKECORE_TARGET} PRIVATE "${CMAKE_CURRENT_LIST_DIR}/../.support/test@hello@2.0.0_static/${CMAKE_SYSTEM_PROCESSOR}-${CMAKE_SYSTEM_NAME}-static/libtest_hello_2_0_0.a")
endif()

