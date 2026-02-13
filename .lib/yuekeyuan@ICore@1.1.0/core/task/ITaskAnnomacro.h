#pragma once

#include "core/config/IConfigPreProcessor.h"

// catagory
#define $EnableCatagory(catagoryName) \
    PP_NORMAL_CONTEXT_CONFIG(EnableCatagory_##catagoryName, /CATAGORY_ENABLE_STATE_##catagoryName, true)

#define $DisableCatagory(catagoryName) \
    PP_NORMAL_CONTEXT_CONFIG(DisableCatagory_##catagoryName, /CATAGORY_ENABLE_STATE/##catagoryName, false)

// task
#define $EnableTask(catagoryName, taskName) \
    PP_NORMAL_CONTEXT_CONFIG(EnableTask_##catagoryName##_##taskName, /TASK_ENABLE_STATE/##catagoryName##/##taskName, true)

#define $DisableTask(catagoryName, taskName) \
    PP_NORMAL_CONTEXT_CONFIG(DisableTask_##catagoryName##_##taskName, /TASK_ENABLE_STATE/##catagoryName##/##taskName, false)
