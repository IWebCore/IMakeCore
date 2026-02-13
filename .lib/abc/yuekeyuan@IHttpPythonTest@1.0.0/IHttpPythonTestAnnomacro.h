#pragma once

#include "core/config/IConfigPreProcessor.h"

#define $EnableHttpPythonTest(boolValue)   \
    PP_NORMAL_CONTEXT_CONFIG(IHttpPythonTest_EnabledHttpPythonTest, /test/pytest/enabled, boolValue)

#define $SetHttpPythonScriptDir(stringValue)   \
    PP_NORMAL_CONTEXT_CONFIG(IHttpPythonTest_SetHttpPythonScriptDir, /test/pytest/scriptDir, #stringValue)

