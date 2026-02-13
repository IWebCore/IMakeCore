#pragma once

#include "core/config/IConfigPreProcessor.h"

#define $EnableUnitTest(boolValue)   \
    PP_NORMAL_CONTEXT_CONFIG(IHttpUnitTest_EnabledUnitTest, /test/unitTest/enabled, boolValue)

#define $EnableFunctionTest(boolValue)  \
    PP_NORMAL_CONTEXT_CONFIG(IHttpUnitTest_EnabledUnitTest, /test/functionTest/enabled, boolValue)

#define $EnableIntegrationTest(boolValue)   \
    PP_NORMAL_CONTEXT_CONFIG(IHttpUnitTest_EnabledUnitTest, /test/integrationTest/enabled, boolValue)

#define $EnableTaskOutput(value)    \
    PP_PRIVILIGE_CONTEXT_CONFIG(EnableTaskOutput_taskOut, /task/taskOutputEnabled, value)

#define $SetAppThreadCount(count)   \
    PP_PRIVILIGE_CONTEXT_CONFIG(SystemSetThreadCount, /system/threadCount, count)
