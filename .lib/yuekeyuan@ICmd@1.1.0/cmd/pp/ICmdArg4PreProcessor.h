#pragma once

#include "core/util/IPreProcessorUtil.h"
#include "cmd/pp/ICmdArgXPreProcessor.h"

#define $CmdArg4Declare(TYPE, NAME) \
    PP_CMD_ARG_X_DECLARE(TYPE, NAME, 4)

#define $CmdArg4(TYPE, NAME)    \
    $CmdArg4Declare(TYPE, NAME) \
    TYPE NAME {};

#define $CmdArg4PreHandle(Func) \
    Q_CLASSINFO( PP_CMD_ARG_X_PRE_HANDLE(4), #Func) \
    Q_INVOKABLE

#define $CmdArg4PostHandle(Func)    \
    Q_CLASSINFO( PP_CMD_ARG_X_POST_HANDLE(4), #Func)    \
    Q_INVOKABLE

#define $CmdArg4Nullable  \
    Q_CLASSINFO(PP_CMD_ARG_X_NULLABLE(4), "true")

#define $CmdArg4Memo(Memo)    \
    Q_CLASSINFO(PP_STRING( ICmdArg4Memo$$$ ), Memo)
