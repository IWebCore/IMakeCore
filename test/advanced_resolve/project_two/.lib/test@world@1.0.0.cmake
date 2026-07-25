# SYSTEM AUTO GENERATED DO NOT EDIT!!!
# test@world@1.0.0
# Test library that depends on hello

set(current_lib_path "C:/Users/Yue/IMakeCore/test/advanced_resolve/.lib/test@world@1.0.0")

target_include_directories(${IMAKECORE_TARGET} PRIVATE
    "${current_lib_path}"
)

target_sources(${IMAKECORE_TARGET} PRIVATE
    "${current_lib_path}/world.cpp"
)

