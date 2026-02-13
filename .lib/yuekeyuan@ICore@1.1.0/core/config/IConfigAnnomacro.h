#pragma once

#include "IConfigPreProcessor.h"

// enable config files scan
#define $EnableConfigFiles(boolValue)    \
    PP_NORMAL_CONTEXT_CONFIG(EnableConfigFiles, /config/enableConfigFiles, boolValue)

// config file scan path
#define $SetConfigFilePaths_(N) $SetConfigFilePaths_##N
#define $SetConfigFilePaths_EVAL(N) $SetConfigFilePaths_(N)
#define $SetConfigFilePaths(...) PP_EXPAND( $SetConfigFilePaths_EVAL(PP_EXPAND( PP_NARG(__VA_ARGS__) ))(__VA_ARGS__) )

#define $SetConfigFilePaths_1(path1_) \
    PP_NORMAL_CONTEXT_CONFIG(SetConfigFilePaths_1, /config/configFilePaths/1, path1_)

#define $SetConfigFilePaths_2(path1_, path2_) \
    $SetConfigFilePaths_1(path1_) \
    PP_NORMAL_CONTEXT_CONFIG(SetConfigFilePaths_2, /config/configFilePaths/2, path2_)

#define $SetConfigFilePaths_3(path1_, path2_, path3_) \
    $SetConfigFilePaths_2(path1_, path2_) \
    PP_NORMAL_CONTEXT_CONFIG(SetConfigFilePaths_3, /config/configFilePaths/3, path3_)

#define $SetConfigFilePaths_4(path1_, path2_, path3_, path4_) \
    $SetConfigFilePaths_3(path1_, path2_, path3_) \
    PP_NORMAL_CONTEXT_CONFIG(SetConfigFilePaths_4, /config/configFilePaths/4, path4_)

#define $SetConfigFilePaths_5(path1_, path2_, path3_, path4_, path5_) \
    $SetConfigFilePaths_4(path1_, path2_, path3_, path4_) \
   PP_NORMAL_CONTEXT_CONFIG(SetConfigFilePaths_5, /config/configFilePaths/5, path5_)

#define $SetConfigFilePaths_6(path1_, path2_, path3_, path4_, path5_, path6_) \
    $SetConfigFilePaths_5(path1_, path2_, path3_, path4_, path5_) \
    PP_NORMAL_CONTEXT_CONFIG(SetConfigFilePaths_6, config/configFilePaths/6, path6_)

#define $SetConfigFilePaths_7(path1_, path2_, path3_, path4_, path5_, path6_, path7_) \
    $SetConfigFilePaths_6(path1_, path2_, path3_, path4_, path5_, path6_) \
    PP_NORMAL_CONTEXT_CONFIG(SetConfigFilePaths_7, /config/configFilePaths/7, path7_)

#define $SetConfigFilePaths_8(path1_, path2_, path3_, path4_, path5_, path6_, path7_, path8_) \
    $SetConfigFilePaths_7(path1_, path2_, path3_, path4_, path5_, path6_, path7_) \
    PP_NORMAL_CONTEXT_CONFIG(SetConfigFilePaths_8, config/configFilePaths/8, path8_)

#define $SetConfigFilePaths_9(path1_, path2_, path3_, path4_, path5_, path6_, path7_, path8_, path9_) \
    $SetConfigFilePaths_8(path1_, path2_, path3_, path4_, path5_, path6_, path7_, path8_) \
    PP_NORMAL_CONTEXT_CONFIG(SetConfigFilePaths_9, /config/configFilePaths/9, path9_)

// default config usage
#define $EnableDefaultConfigFiles   \
    $EnableConfigFiles(true)   \
    $SetConfigFilePaths(":/config/")

