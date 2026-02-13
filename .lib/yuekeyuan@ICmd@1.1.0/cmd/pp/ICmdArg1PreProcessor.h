#pragma once

#include "core/util/IPreProcessorUtil.h"
#include "cmd/pp/ICmdArgXPreProcessor.h"

#define $CmdArg1Declare(TYPE, NAME) \
    PP_CMD_ARG_X_DECLARE(TYPE, NAME, 1)

#define $CmdArg1(TYPE, NAME)    \
    $CmdArg1Declare(TYPE, NAME) \
    TYPE NAME {};

#define $CmdArg1PreHandle(Func) \
    Q_CLASSINFO( PP_CMD_ARG_X_PRE_HANDLE(1), #Func) \
    Q_INVOKABLE

#define $CmdArg1PostHandle(Func)    \
    Q_CLASSINFO( PP_CMD_ARG_X_POST_HANDLE(1), #Func)    \
    Q_INVOKABLE

#define $CmdArg1Nullable  \
    Q_CLASSINFO(PP_CMD_ARG_X_NULLABLE(1), "true")

#define $CmdArg1Memo(Memo)    \
    Q_CLASSINFO(PP_STRING( ICmdArg1Memo$$$ ), Memo)

