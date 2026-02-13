#pragma once

#include "core/util/IPreProcessorUtil.h"

// $CmdArgs
#define PP_CMD_ARGS_ARGUMENT(NAME)   \
    PP_STRING( ICmdArgsArgument$$$ ## NAME )


#define $CmdArgsDeclare(TYPE, NAME)                                     \
    Q_CLASSINFO( PP_CMD_ARGS_ARGUMENT(NAME), #NAME)                      \
    Q_PROPERTY(TYPE NAME MEMBER NAME)                                   \
    Q_INVOKABLE void $set_value_ ## NAME(const QStringList& raws){      \
        detail::setValue< TYPE >( NAME, raws );                         \
    }

#define $CmdArgs(TYPE, NAME)                                            \
    $CmdArgsDeclare(TYPE, NAME)                                          \
    TYPE NAME {};

#define PP_CMD_ARGS_NULLABLE(NAME)  \
    PP_STRING( ICmdArgsNullable$$$ ## NAME)

#define $CmdArgsNullable(NAME)  \
    Q_CLASSINFO(PP_CMD_ARGS_NULLABLE(NAME), #NAME)


// $CmdArgsPreHandle
#define PP_CMD_ARGS_PRE_HANDLE(name)         \
    PP_STRING(ICmdArgsPreHandle$$$ ## name)

#define PP_CMD_ARGS_PRE_HANDLE_DEFAULT_FUNCTION(name)    \
    PP_STRING(name ## _PreHandle)

#define $CmdArgsPreHandle_1(name) \
    Q_CLASSINFO(PP_CMD_ARGS_PRE_HANDLE(name), PP_CMD_ARGS_PRE_HANDLE_DEFAULT_FUNCTION( name ) )    \
    Q_INVOKABLE

#define $CmdArgsPreHandle_2(name, func) \
    Q_CLASSINFO(PP_CMD_ARGS_PRE_HANDLE(name), #func )    \
    Q_INVOKABLE

#define $CmdArgsPreHandle_(N) $CmdArgsPreHandle_##N
#define $CmdArgsPreHandle_EVAL(N) $CmdArgsPreHandle_(N)
#define $CmdArgsPreHandle(...) PP_EXPAND( $CmdArgsPreHandle_EVAL(PP_EXPAND( PP_NARG(__VA_ARGS__) ))(__VA_ARGS__) )


// $CmdArgsPostHandle
#define PP_CMD_ARGS_POSGT_HANDLE(name)         \
    PP_STRING(ICmdArgsPostHandle$$$ ## name)

#define PP_CMD_ARGS_POSGT_HANDLE_DEFAULT_FUNCTION(name)    \
    PP_STRING(name ## _PostHandle)

#define $CmdArgsPostHandle_1(name) \
    Q_CLASSINFO(PP_CMD_ARGS_POSGT_HANDLE(name), PP_CMD_ARGS_POSGT_HANDLE_DEFAULT_FUNCTION( name ) )    \
    Q_INVOKABLE

#define $CmdArgsPostHandle_2(name, func) \
    Q_CLASSINFO(PP_CMD_ARGS_POSGT_HANDLE(name), #func )    \
    Q_INVOKABLE

#define $CmdArgsPostHandle_(N) $CmdArgsPostHandle_##N
#define $CmdArgsPostHandle_EVAL(N) $CmdArgsPostHandle_(N)
#define $CmdArgsPostHandle(...) PP_EXPAND( $CmdArgsPostHandle_EVAL(PP_EXPAND( PP_NARG(__VA_ARGS__) ))(__VA_ARGS__) )

// memo
#define $CmdArgsMemo(Opt, Memo)   \
    Q_CLASSINFO(PP_STRING( ICmdArgsMemo$$$ ## Opt), Memo)




