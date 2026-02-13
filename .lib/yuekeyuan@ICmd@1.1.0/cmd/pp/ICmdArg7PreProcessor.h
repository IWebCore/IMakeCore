#pragma once

#include "core/util/IPreProcessorUtil.h"
#include "cmd/pp/ICmdArgXPreProcessor.h"

#define $CmdArg7Declare(TYPE, NAME) \
    PP_CMD_ARG_X_DECLARE(TYPE, NAME, 7)

#define $CmdArg7(TYPE, NAME)    \
    $CmdArg7Declare(TYPE, NAME) \
    TYPE NAME {};

#define $CmdArg7PreHandle(Func) \
    Q_CLASSINFO( PP_CMD_ARG_X_PRE_HANDLE(7), #Func) \
    Q_INVOKABLE

#define $CmdArg7PostHandle(Func)    \
    Q_CLASSINFO( PP_CMD_ARG_X_POST_HANDLE(7), #Func)    \
    Q_INVOKABLE

#define $CmdArg7Nullable  \
    Q_CLASSINFO(PP_CMD_ARG_X_NULLABLE(7), "true")

#define $CmdArg7Memo(Memo)    \
    Q_CLASSINFO(PP_STRING( ICmdArg7Memo$$$ ), Memo)
