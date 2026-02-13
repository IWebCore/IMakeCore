#pragma once

#include "core/util/IPreProcessorUtil.h"
#include "core/unit/IGadgetUnit.h"

#define PP_AS_CMD_CLASS_MAPPING(index)    \
    PP_STRING(IAsCmdClassMapping$$$ ## index)

#define $AsCmd_1(arg)  \
    Q_CLASSINFO( PP_AS_CMD_CLASS_MAPPING(1), #arg) \
    PP_GADGET_STATIC_META_OBJECT_FUNC

#define $AsCmd_2(arg, arg1)  \
    $AsCmd(arg)
    Q_CLASSINFO( PP_AS_CMD_CLASS_MAPPING(2), #arg1)

#define $AsCmd_3(arg, arg1, arg2)  \
    $AsCmd(arg, arg1) \
    Q_CLASSINFO( PP_AS_CMD_CLASS_MAPPING(3), #arg2)

#define $AsCmd_4(arg, arg1, arg2, arg3)  \
    $AsCmd(arg, arg1, arg2) \
    Q_CLASSINFO( PP_AS_CMD_CLASS_MAPPING(4), #arg3)

#define $AsCmd_5(arg, arg1, arg2, arg3, arg4)  \
    $AsCmd(arg, arg1, arg2, arg3) \
    Q_CLASSINFO( PP_AS_CMD_CLASS_MAPPING(5), #arg4)

#define $AsCmd_6(arg, arg1, arg2, arg3, arg4, arg5)  \
    $AsCmd(arg, arg1, arg2, arg3, arg4) \
    Q_CLASSINFO( PP_AS_CMD_CLASS_MAPPING(6), #arg5)

#define $AsCmd_7(arg, arg1, arg2, arg3, arg4, arg5, arg6)  \
    $AsCmd(arg, arg1, arg2, arg3, arg4, arg5) \
    Q_CLASSINFO( PP_AS_CMD_CLASS_MAPPING(7), #arg6)

#define $AsCmd_8(arg, arg1, arg2, arg3, arg4, arg5, arg6, arg7)  \
    $AsCmd(arg, arg1, arg2, arg3, arg4, arg5, arg6) \
    Q_CLASSINFO( PP_AS_CMD_CLASS_MAPPING(7), #arg7)

#define $AsCmd_9(arg, arg1, arg2, arg3, arg4, arg5, arg6, arg7, arg8)  \
    $AsCmd(arg, arg1, arg2, arg3, arg4, arg5, arg6, arg7) \
    Q_CLASSINFO( PP_AS_CMD_CLASS_MAPPING(8), #arg8)

#define $AsCmd_(N) $AsCmd_##N
#define $AsCmd_EVAL(N) $AsCmd_(N)
#define $AsCmd(...) PP_EXPAND( $AsCmd_EVAL(PP_EXPAND( PP_NARG(__VA_ARGS__) ))(__VA_ARGS__) )
