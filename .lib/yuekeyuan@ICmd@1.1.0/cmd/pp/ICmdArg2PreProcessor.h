#pragma once

#include "core/util/IPreProcessorUtil.h"
#include "cmd/pp/ICmdArgXPreProcessor.h"

#define $CmdArg2Declare(TYPE, NAME) \
    PP_CMD_ARG_X_DECLARE(TYPE, NAME, 2)

#define $CmdArg2(TYPE, NAME)    \
    $CmdArg2Declare(TYPE, NAME) \
    TYPE NAME {};

#define $CmdArg2PreHandle(Func) \
    Q_CLASSINFO( PP_CMD_ARG_X_PRE_HANDLE(2), #Func) \
    Q_INVOKABLE

#define $CmdArg2PostHandle(Func)    \
    Q_CLASSINFO( PP_CMD_ARG_X_POST_HANDLE(2), #Func)    \
    Q_INVOKABLE

#define $CmdArg2Nullable  \
    Q_CLASSINFO(PP_CMD_ARG_X_NULLABLE(2), "true")

#define $CmdArg2Memo(Memo)    \
    Q_CLASSINFO(PP_STRING( ICmdArg2Memo$$$ ), Memo)
