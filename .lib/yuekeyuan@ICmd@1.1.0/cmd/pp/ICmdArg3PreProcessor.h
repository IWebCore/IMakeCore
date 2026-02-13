#pragma once

#include "core/util/IPreProcessorUtil.h"
#include "cmd/pp/ICmdArgXPreProcessor.h"

#define $CmdArg3Declare(TYPE, NAME) \
    PP_CMD_ARG_X_DECLARE(TYPE, NAME, 3)

#define $CmdArg3(TYPE, NAME)    \
    $CmdArg3Declare(TYPE, NAME) \
    TYPE NAME {};

#define $CmdArg3PreHandle(Func) \
    Q_CLASSINFO( PP_CMD_ARG_X_PRE_HANDLE(3), #Func) \
    Q_INVOKABLE

#define $CmdArg3PostHandle(Func)    \
    Q_CLASSINFO( PP_CMD_ARG_X_POST_HANDLE(3), #Func)    \
    Q_INVOKABLE

#define $CmdArg3Nullable  \
    Q_CLASSINFO(PP_CMD_ARG_X_NULLABLE(3), "true")

#define $CmdArg3Memo(Memo)    \
    Q_CLASSINFO(PP_STRING( ICmdArg3Memo$$$ ), Memo)
