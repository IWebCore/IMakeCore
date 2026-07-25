# SYSTEM AUTO GENERATED DO NOT EDIT!!!
# test@world@1.0.0
# Test library that depends on hello

set(current_lib_path "C:/Users/Yue/IMakeCore/test/static_chain/.lib/test@world@1.0.0")

target_include_directories(${IMAKECORE_TARGET} PRIVATE
    "${current_lib_path}"
)

if(MSVC)
    target_link_libraries(${IMAKECORE_TARGET} PRIVATE "${CMAKE_CURRENT_LIST_DIR}/../.support/test@world@1.0.0_static/${CMAKE_SYSTEM_PROCESSOR}-${CMAKE_SYSTEM_NAME}-static/test_world_1_0_0.lib")
else()
    target_link_libraries(${IMAKECORE_TARGET} PRIVATE "${CMAKE_CURRENT_LIST_DIR}/../.support/test@world@1.0.0_static/${CMAKE_SYSTEM_PROCESSOR}-${CMAKE_SYSTEM_NAME}-static/libtest_world_1_0_0.a")
endif()

