#pragma once

#include "core/util/IPreProcessorUtil.h"
#include "cmd/pp/ICmdArgXPreProcessor.h"

#define $CmdArg5Declare(TYPE, NAME) \
    PP_CMD_ARG_X_DECLARE(TYPE, NAME, 5)

#define $CmdArg5(TYPE, NAME)    \
    $CmdArg5Declare(TYPE, NAME) \
    TYPE NAME {};

#define $CmdArg5PreHandle(Func) \
    Q_CLASSINFO( PP_CMD_ARG_X_PRE_HANDLE(5), #Func) \
    Q_INVOKABLE

#define $CmdArg5PostHandle(Func)    \
    Q_CLASSINFO( PP_CMD_ARG_X_POST_HANDLE(5), #Func)    \
    Q_INVOKABLE

#define $CmdArg5Nullable  \
    Q_CLASSINFO(PP_CMD_ARG_X_NULLABLE(5), "true")

#define $CmdArg5Memo(Memo)    \
    Q_CLASSINFO(PP_STRING( ICmdArg5Memo$$$ ), Memo)
