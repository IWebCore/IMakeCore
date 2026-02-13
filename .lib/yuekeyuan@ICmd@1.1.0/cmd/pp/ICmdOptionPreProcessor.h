#pragma once

#include "core/util/IPreProcessorUtil.h"

#define PP_CMD_OPTION(NAME)  \
    PP_STRING( ICmdOption$$$ ## NAME)

#define $CmdOption(Opt) \
    Q_CLASSINFO( PP_CMD_OPTION(Opt), #Opt)    \
    Q_PROPERTY(bool Opt MEMBER Opt )   \
    bool Opt {false};

// option pre handle
#define PP_CMD_PRE_OPTION(name)         \
    PP_STRING(ICmdOptionPreHandle$$$ ## name)

#define PP_CMD_PRE_OPTION_DEFAULT_FUNCTION(name)    \
    PP_STRING(name ## _PreHandle)

#define $CmdOptionPreHandle_1(name) \
    Q_CLASSINFO(PP_CMD_PRE_OPTION(name), PP_CMD_PRE_OPTION_DEFAULT_FUNCTION( name ) )    \
    Q_INVOKABLE

#define $CmdOptionPreHandle_2(name, func)  \
    Q_CLASSINFO(PP_CMD_PRE_OPTION(name), #func )    \
    Q_INVOKABLE

#define $CmdOptionPreHandle_(N) $CmdOptionPreHandle_##N
#define $CmdOptionPreHandle_EVAL(N) $CmdOptionPreHandle_(N)
#define $CmdOptionPreHandle(...) PP_EXPAND( $CmdOptionPreHandle_EVAL(PP_EXPAND( PP_NARG(__VA_ARGS__) ))(__VA_ARGS__) )

// option post handle
#define PP_CMD_POST_OPTION(name)         \
    PP_STRING(ICmdOptionPostHandle$$$ ## name)

#define PP_CMD_POST_OPTION_DEFAULT_FUNCTION(name)    \
    PP_STRING(name ## _PostHandle)

#define $CmdOptionPostHandle_1(name) \
    Q_CLASSINFO(PP_CMD_POST_OPTION(name), PP_CMD_POST_OPTION_DEFAULT_FUNCTION( name ) )    \
    Q_INVOKABLE

#define $CmdOptionPostHandle_2(name, func) \
    Q_CLASSINFO(PP_CMD_POST_OPTION(name), #func)    \
    Q_INVOKABLE

#define $CmdOptionPostHandle_(N) $CmdOptionPostHandle_##N
#define $CmdOptionPostHandle_EVAL(N) $CmdOptionPostHandle_(N)
#define $CmdOptionPostHandle(...) PP_EXPAND( $CmdOptionPostHandle_EVAL(PP_EXPAND( PP_NARG(__VA_ARGS__) ))(__VA_ARGS__) )

// Option required
#define PP_CMD_OPTION_REQUIRED(name)    \
    PP_STRING(ICmdOptionRequired$$$ ## name)

#define $CmdOptionRequired(name)    \
    Q_CLASSINFO(PP_CMD_OPTION_REQUIRED(name), "true")

// Option shortName
#define PP_CMD_OPTION_SHORT_NAME(Opt)   \
    PP_STRING(ICmdOptionShortName$$$ ## Opt)

#define $CmdOptionShortName(Opt, Name)  \
    Q_CLASSINFO(PP_CMD_OPTION_SHORT_NAME(Opt), #Name)

// memo
#define $CmdOptionMemo(Opt, Memo)   \
    Q_CLASSINFO(PP_STRING( ICmdOptionMemo$$$ ## Opt), Memo)

// no value
#define $CmdOptionNoValue(Opt)  \
    Q_CLASSINFO(PP_STRING( ICmdOptionNoValue$$$ ## Opt ), "true")

// arg list // this will be latter
