#pragma once

#include "core/util/IPreProcessorUtil.h"
#include "cmd/pp/ICmdArgXPreProcessor.h"

#define $CmdArg8Declare(TYPE, NAME) \
    PP_CMD_ARG_X_DECLARE(TYPE, NAME, 8)

#define $CmdArg8(TYPE, NAME)    \
    $CmdArg8Declare(TYPE, NAME) \
    TYPE NAME {};

#define $CmdArg8PreHandle(Func) \
    Q_CLASSINFO( PP_CMD_ARG_X_PRE_HANDLE(8), #Func) \
    Q_INVOKABLE

#define $CmdArg8PostHandle(Func)    \
    Q_CLASSINFO( PP_CMD_ARG_X_POST_HANDLE(8), #Func)    \
    Q_INVOKABLE

#define $CmdArg8Nullable  \
    Q_CLASSINFO(PP_CMD_ARG_X_NULLABLE(8), "true")

#define $CmdArg8Memo(Memo)    \
    Q_CLASSINFO(PP_STRING( ICmdArg8Memo$$$ ), Memo)
