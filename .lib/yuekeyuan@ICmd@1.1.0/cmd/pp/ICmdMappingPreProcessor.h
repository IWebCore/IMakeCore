#pragma once

#include "core/util/IPreProcessorUtil.h"


// cmd mapping
#define PP_CMD_METHOD_MAPPING(name)   \
    PP_STRING(IAsCmdMethodMapping$$$ ## name)

#define PP_CMD_METHOD_ARG_MAPPING(name, index)   \
    PP_STRING(IAsCmdMethodArgMapping$$$ ## name ## $$$ ## index)

#define $CmdMapping_1(funName)    \
    Q_CLASSINFO( PP_CMD_METHOD_MAPPING(funName), #funName)   \
    Q_CLASSINFO( PP_CMD_METHOD_ARG_MAPPING(funName, 1), #funName) \
    Q_INVOKABLE

#define $CmdMapping_2(funName, arg1)    \
    Q_CLASSINFO( PP_CMD_METHOD_MAPPING(funName), #funName)   \
    Q_CLASSINFO( PP_CMD_METHOD_ARG_MAPPING(funName, 1), #arg1) \
    Q_INVOKABLE

#define $CmdMapping_3(funName, arg1, arg2)    \
    Q_CLASSINFO( PP_CMD_METHOD_ARG_MAPPING(funName, 2), #arg2) \
    $CmdMapping_2(funName, arg1)

#define $CmdMapping_4(funName, arg1, arg2, arg3)    \
    Q_CLASSINFO( PP_CMD_METHOD_ARG_MAPPING(funName, 3), #arg3) \
    $CmdMapping_3(funName, arg1, arg2)

#define $CmdMapping_5(funName, arg1, arg2, arg3, arg4)    \
    Q_CLASSINFO( PP_CMD_METHOD_ARG_MAPPING(funName, 4), #arg4) \
    $CmdMapping_4(funName, arg1, arg2, arg3)

#define $CmdMapping_6(funName, arg1, arg2, arg3, arg4, arg5)    \
    Q_CLASSINFO( PP_CMD_METHOD_ARG_MAPPING(funName, 5), #arg5) \
    $CmdMapping_5(funName, arg1, arg2, arg3, arg4)

#define $CmdMapping_7(funName, arg1, arg2, arg3, arg4, arg5, arg6)    \
    Q_CLASSINFO( PP_CMD_METHOD_ARG_MAPPING(funName, 6), #arg6) \
    $CmdMapping_6(funName, arg1, arg2, arg3, arg4, arg5)

#define $CmdMapping_8(funName, arg1, arg2, arg3, arg4, arg5, arg6, arg7)    \
    Q_CLASSINFO( PP_CMD_METHOD_ARG_MAPPING(funName, 7), #arg7) \
    $CmdMapping_7(funName, arg1, arg2, arg3, arg4, arg5, arg6)

#define $CmdMapping_9(funName, arg1, arg2, arg3, arg4, arg5, arg6, arg7, arg8)    \
    Q_CLASSINFO( PP_CMD_METHOD_ARG_MAPPING(funName, 8), #arg8) \
    $CmdMapping_8(funName, arg1, arg2, arg3, arg4, arg5, arg6, arg7)

#define $CmdMapping_(N) $CmdMapping_##N
#define $CmdMapping_EVAL(N) $CmdMapping_(N)
#define $CmdMapping(...) PP_EXPAND( $CmdMapping_EVAL(PP_EXPAND( PP_NARG(__VA_ARGS__) ))(__VA_ARGS__) )

// memo
#define $CmdMappingMemo(funName, Memo)   \
    Q_CLASSINFO(PP_STRING( ICmdMappingMemo$$$ ## funName), Memo)
