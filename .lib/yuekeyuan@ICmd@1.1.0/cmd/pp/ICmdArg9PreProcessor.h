#pragma once

#include "core/util/IPreProcessorUtil.h"
#include "cmd/pp/ICmdArgXPreProcessor.h"

#define $CmdArg9Declare(TYPE, NAME) \
    PP_CMD_ARG_X_DECLARE(TYPE, NAME, 9)

#define $CmdArg9(TYPE, NAME)    \
    $CmdArg9Declare(TYPE, NAME) \
    TYPE NAME {};

#define $CmdArg9PreHandle(Func) \
    Q_CLASSINFO( PP_CMD_ARG_X_PRE_HANDLE(9), #Func) \
    Q_INVOKABLE

#define $CmdArg9PostHandle(Func)    \
    Q_CLASSINFO( PP_CMD_ARG_X_POST_HANDLE(9), #Func)    \
    Q_INVOKABLE

#define $CmdArg9Nullable  \
    Q_CLASSINFO(PP_CMD_ARG_X_NULLABLE(9), "true")

#define $CmdArg9Memo(Memo)    \
    Q_CLASSINFO(PP_STRING( ICmdArg9Memo$$$ ), Memo)
