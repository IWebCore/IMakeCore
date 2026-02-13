#pragma once

#include "core/util/IPreProcessorUtil.h"
#include "core/util/IJsonUtil.h"
#include "core/bean/IBeanTypeManage.h"

#define PP_BeanFieldDeclare(type, name) \
    Q_INVOKABLE IJson $##name##_toJsonValue() const {                                               \
        return IJsonUtil::toJson( name );                                                           \
    }                                                                                               \
    Q_INVOKABLE bool $##name##_fromJsonValue(const IJson& json) {                                   \
        return IJsonUtil::fromJson( name, json);                                                    \
    }                                                                                               \
public:

#define PP_BeanFieldDeclareAfterWrite(type, name, writeFunc)                                \
    Q_INVOKABLE IJson $##name##_toJsonValue() const {                                               \
        return IJsonUtil::toJson( name );                                                           \
    }                                                                                               \
    Q_INVOKABLE bool $##name##_fromJsonValue(const IJson& json) {                                   \
        auto val = IJsonUtil::fromJson( name, json);                                                \
        if(val) writeFunc();                                                                        \
        return val;                                                                                 \
    }                                                                                               \
public:

#define PP_BeanFieldDeclareBeforeRead(type, name, readFunc)                                 \
    Q_INVOKABLE IJson $##name##_toJsonValue() const {                                               \
        readFunc();                                                                                 \
        return IJsonUtil::toJson( name );                                                           \
    }                                                                                               \
    Q_INVOKABLE bool $##name##_fromJsonValue(const IJson& json) {                                   \
        return IJsonUtil::fromJson( name, json);                                                    \
    }                                                                                               \
public:

#define PP_BeanFieldDeclareBeforeReadAfterWrite(type, name, readFunc, writeFunc)            \
    Q_INVOKABLE IJson $##name##_toJsonValue() const {                                               \
        readFunc();                                                                                 \
        return IJsonUtil::toJson( name );                                                           \
    }                                                                                               \
    Q_INVOKABLE bool $##name##_fromJsonValue(const IJson& json) {                                   \
        auto val = IJsonUtil::fromJson( name, json);                                                \
        if(val) writeFunc();                                                                        \
        return val;                                                                                 \
    }                                                                                               \
public:


#define $BeanFieldDeclare(type, name)                                                               \
private:                                                                                            \
    Q_PROPERTY(type name MEMBER name)                                                               \
    PP_BeanFieldDeclare(type, name)

#define $BeanFieldDeclareWithRead(type, name, readFunc)                                             \
    Q_PROPERTY(type name MEMBER name)                                                               \
    PP_BeanFieldDeclareBeforeRead(type, name, readFunc)

#define $BeanFieldDeclareWithWrite(type, name, writeFunc)                                           \
    Q_PROPERTY(type name MEMBER name)                                                               \
    PP_BeanFieldDeclareAfterWrite(type, name, writeFunc)

#define $BeanFieldDeclareWithReadWrite(type, name, readFunc, WriteFunc)                             \
    Q_PROPERTY(type name MEMBER name READ readFunc WRITE writeFunc)                                 \
    PP_BeanFieldDeclareBeforeReadAfterWrite(type, name, readFunc, WriteFunc)

#define $BeanFieldRequired(name)    \
    Q_CLASSINFO(PP_STRING( $beanfieldrequired_ ## name ), #name)

#define $BeanJsonValidator(name) \
    Q_CLASSINFO(PP_STRING( $beanjsonvalidator__ ) , #name)   \
    Q_INVOKABLE

#define $BeanField_2(type, name) \
    type name {};                \
    $BeanFieldDeclare(type, name)

#define $BeanField_3(type, name, value1) \
    $BeanFieldDeclare(type, name) \
    type name {value1};

#define $BeanField_4(type, name, value1, value2) \
    $BeanFieldDeclare(type, name) \
    type name {value1, value2};

#define $BeanField_5(type, name, value1, value2, value3) \
    $BeanFieldDeclare(type, name) \
    type name {value1, value2, value3};

#define $BeanField_6(type, name, value1, value2, value3, value4) \
    $BeanFieldDeclare(type, name) \
    type name {value1, value2, value3, value4};

#define $BeanField_7(type, name, value1, value2, value3, value4, value5) \
    $BeanFieldDeclare(type, name) \
    type name {value1, value2, value3, value4, value5};

#define $BeanField_8(type, name, value1, value2, value3, value4, value5, value6) \
    $BeanFieldDeclare(type, name) \
    type name {value1, value2, value3, value4, value5, value6};

#define $BeanField_9(type, name, value1, value2, value3, value4, value5, value6, value7) \
    $BeanFieldDeclare(type, name) \
    type name {value1, value2, value3, value4, value5, value6, value7};

#define $BeanField_10(type, name, value1, value2, value3, value4, value5, value6, value7, value8) \
    $BeanFieldDeclare(type, name) \
    type name {value1, value2, value3, value4, value5, value6, value7, value8};

#define $BeanField_11(type, name, value1, value2, value3, value4, value5, value6, value7, value8, value9) \
    $BeanFieldDeclare(type, name) \
    type name {value1, value2, value3, value4, value5, value6, value7, value8, value9};

#define $BeanField_12(type, name, value1, value2, value3, value4, value5, value6, value7, value8, value9, value10) \
    $BeanFieldDeclare(type, name) \
    type name {value1, value2, value3, value4, value5, value6, value7, value8, value9, value10};

#define $BeanField_(N) $BeanField_##N
#define $BeanField_EVAL(N) $BeanField_(N)
#define $BeanField(...) PP_EXPAND( $BeanField_EVAL(PP_EXPAND( PP_NARG(__VA_ARGS__) ))(__VA_ARGS__) )

