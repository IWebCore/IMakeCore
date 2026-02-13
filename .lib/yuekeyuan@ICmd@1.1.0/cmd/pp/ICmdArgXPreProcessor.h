#pragma once

#include "core/util/IPreProcessorUtil.h"

// $CmdArgX
#define PP_CMD_ARG_X_ARGUMENT(NAME, INDEX) \
    PP_STRING( ICmdArgXArgument$$$ ## INDEX ## $$$ ## NAME)

#define PP_CMD_ARG_X_DECLARE(TYPE, NAME, INDEX)  \
    Q_CLASSINFO( PP_CMD_ARG_X_ARGUMENT(NAME, INDEX), #NAME)  \
    Q_PROPERTY(TYPE NAME MEMBER NAME)           \
    Q_INVOKABLE void $set_value_ ## NAME (const QStringList& raws){ \
        detail::setValue< TYPE > (NAME, raws);      \
    }

#define PP_CMD_ARG_X_NULLABLE(INDEX)  \
    PP_STRING( ICmdArgXNullable$$$ ## INDEX )

#define PP_CMD_ARG_X_PRE_HANDLE(INDEX)   \
    PP_STRING( ICmdArgXPreHandle$$$ ## INDEX)

#define PP_CMD_ARG_X_POST_HANDLE(INDEX) \
    PP_STRING( ICmdArgXPostHandle$$$ ## INDEX)
