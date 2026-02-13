#pragma once
#include "core/util/IPreProcessorUtil.h"
#include "core/bean/IBeanPreProcessor.h"

#define $ColumnDeclare(type, name) \
    static constexpr char const * $field_##name = #name ; \
    $BeanFieldDeclare(type, name)

#define $ColumnDeclareWithRead(type, name, readFunc) \
    static constexpr char const * $field_##name = #name ; \
    $BeanFieldDeclareWithRead(type, name, readFunc)

#define $ColumnDeclareWithWrite(type, name, writeFunc) \
    static constexpr char const * $field_##name = #name ; \
    $BeanFieldDeclareWithWrite(type, name, writeFunc)

#define $ColumnDeclareWithReadWrite(type, name, readFunc, writeFunc) \
    static constexpr char const * $field_##name = #name ; \
    $BeanFieldDeclareWithReadWrite(type, name, readFunc, writeFunc)

#define $Column_2(type, name) \
    static constexpr char const * $field_##name = #name ; \
    $BeanField(type, name)

#define $Column_3(type, name, value1) \
    static constexpr char const * $field_##name = #name ; \
    $BeanField(type, name, value1)

#define $Column_4(type, name, value1, value2) \
    static constexpr char const * $field_##name = #name ; \
    $BeanField(type, name, value1, value2)

#define $Column_5(type, name, value1, value2, value3) \
    static constexpr char const * $field_##name = #name ; \
    $BeanField(type, name, value1, value2, value3)

#define $Column_6(type, name, value1, value2, value3, value4) \
    static constexpr char const * $field_##name = #name ; \
    $BeanField(type, name, value1, value2, value3, value4)

#define $Column_7(type, name, value1, value2, value3, value4, value5) \
    static constexpr char const * $field_##name = #name ; \
    $BeanField(type, name, value1, value2, value3, value4, value5)

#define $Column_8(type, name, value1, value2, value3, value4, value5, value6) \
    static constexpr char const * $field_##name = #name ; \
    $BeanField(type, name, value1, value2, value3, value4, value5, value6)

#define $Column_9(type, name, value1, value2, value3, value4, value5, value6, value7) \
    static constexpr char const * $field_##name = #name ; \
    $BeanField(type, name, value1, value2, value3, value4, value5, value6, value7)

#define $Column_10(type, name, value1, value2, value3, value4, value5, value6, value7, value8) \
    static constexpr char const * $field_##name = #name ; \
    $BeanField(type, name, value1, value2, value3, value4, value5, value6, value7, value8)

#define $Column_11(type, name, value1, value2, value3, value4, value5, value6, value7, value8, value9) \
    static constexpr char const * $field_##name = #name ; \
    $BeanField(type, name, value1, value2, value3, value4, value5, value6, value7, value8, value9)

#define $Column_12(type, name, value1, value2, value3, value4, value5, value6, value7, value8, value9, value10) \
    static constexpr char const * $field_##name = #name ; \
    $BeanField(type, name, value1, value2, value3, value4, value5, value6, value7, value8, value9, value10)

#define $Column_(N) $Column_##N
#define $Column_EVAL(N) $Column_(N)
#define $Column(...) PP_EXPAND( $Column_EVAL(PP_EXPAND( PP_NARG(__VA_ARGS__) ))(__VA_ARGS__) )
