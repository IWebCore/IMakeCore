#pragma once

#include "core/util/IPreProcessorUtil.h"

// $CmdOptionValueDeclare
#define $CmdOptionValueDeclare(Opt, Type, Name)                                         \
    Q_CLASSINFO(PP_STRING( ICmdOptionValue$$$ ## Opt ## $$$ # Name), #Name)                           \
    Q_PROPERTY(Type Name MEMBER Name)                                                   \
    Q_INVOKABLE void $set_value_ ## Name (const QStringList& raws)  {                   \
        detail::setValue< Type >( Name, raws);                                          \
    }

// $CmdOptionValue
#define $CmdOptionValue(Opt, Type, Name)    \
    $CmdOptionValueDeclare(Opt, Type, Name)    \
    Type Name {};

// $CmdOptionValuePreHanle
#define PP_CMD_OPTION_VALUE_PRE_HANDLE(name)         \
    PP_STRING(ICmdOptionValuePreHandle$$$ ## name)

#define PP_CMD_OPTION_VALUE_PRE_HANDLE_DEFAULT_FUNCTION(name)    \
    PP_STRING(name ## _PreHandle)

#define $CmdOptionValuePreHandle_1(name) \
    Q_CLASSINFO(PP_CMD_OPTION_VALUE_PRE_HANDLE(name), PP_CMD_OPTION_VALUE_PRE_HANDLE_DEFAULT_FUNCTION( name ) )    \
    Q_INVOKABLE

#define $CmdOptionValuePreHandle_2(name, func)  \
    Q_CLASSINFO(PP_CMD_OPTION_VALUE_PRE_HANDLE(name), func )    \
    Q_INVOKABLE

#define $CmdOptionValuePreHandle_(N) $CmdOptionValuePreHandle_##N
#define $CmdOptionValuePreHandle_EVAL(N) $CmdOptionValuePreHandle_(N)
#define $CmdOptionValuePreHandle(...) PP_EXPAND( $CmdOptionValuePreHandle_EVAL(PP_EXPAND( PP_NARG(__VA_ARGS__) ))(__VA_ARGS__) )


// option post handle
#define PP_CMD_OPTION_VALUE_POST_HANDLE(name)         \
    PP_STRING(ICmdOptionValuePostHandle$$$ ## name)

#define PP_CMD_OPTION_VALUE_POST_HANDLE_DEFAULT_FUNCTION(name)    \
    PP_STRING(name ## _PostHandle)

#define $CmdOptionValuePostHandle_1(name) \
    Q_CLASSINFO(PP_CMD_OPTION_VALUE_POST_HANDLE(name), PP_CMD_OPTION_VALUE_POST_HANDLE_DEFAULT_FUNCTION( name ) )    \
    Q_INVOKABLE

#define $CmdOptionValuePostHandle_2(name, func) \
    Q_CLASSINFO(PP_CMD_OPTION_VALUE_POST_HANDLE(name), func)    \
    Q_INVOKABLE

#define $CmdOptionValuePostHandle_(N) $CmdOptionValuePostHandle_##N
#define $CmdOptionValuePostHandle_EVAL(N) $CmdOptionValuePostHandle_(N)
#define $CmdOptionValuePostHandle(...) PP_EXPAND( $CmdOptionValuePostHandle_EVAL(PP_EXPAND( PP_NARG(__VA_ARGS__) ))(__VA_ARGS__) )

// memo
#define $CmdOptionValueMemo(Opt, Memo)   \
    Q_CLASSINFO(PP_STRING( ICmdOptionValueMemo$$$ ## Opt), Memo)

#define $CmdOptionValueNullable(Opt)
    Q_CLASSINFO(PP_STRING( ICmdOptionValueNullable$$$ ## Opt), "true")

