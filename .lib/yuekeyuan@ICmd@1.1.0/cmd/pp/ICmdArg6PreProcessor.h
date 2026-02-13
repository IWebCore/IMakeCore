#pragma once

#include "core/util/IPreProcessorUtil.h"
#include "cmd/pp/ICmdArgXPreProcessor.h"

#define $CmdArg6Declare(TYPE, NAME) \
    PP_CMD_ARG_X_DECLARE(TYPE, NAME, 6)

#define $CmdArg6(TYPE, NAME)    \
    $CmdArg6Declare(TYPE, NAME) \
    TYPE NAME {};

#define $CmdArg6PreHandle(Func) \
    Q_CLASSINFO( PP_CMD_ARG_X_PRE_HANDLE(6), #Func) \
    Q_INVOKABLE

#define $CmdArg6PostHandle(Func)    \
    Q_CLASSINFO( PP_CMD_ARG_X_POST_HANDLE(6), #Func)    \
    Q_INVOKABLE

#define $CmdArg6Nullable  \
    Q_CLASSINFO(PP_CMD_ARG_X_NULLABLE(6), "true")

#define $CmdArg6Memo(Memo)    \
    Q_CLASSINFO(PP_STRING( ICmdArg6Memo$$$ ), Memo)
