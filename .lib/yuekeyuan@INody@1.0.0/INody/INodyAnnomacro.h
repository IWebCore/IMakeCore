#pragma once

#include "core/config/IConfigPreProcessor.h"

#define $setHttpNodyEnabled( boolValue )  \
    PP_PROFILE_CONFIG(SetHttpAssetsPath, /http/nody/enabled, boolValue)

#define $SetHttpNodyPath( path_str )  \
    PP_PROFILE_CONFIG(SetHttpNodyPath, /http/nody/path, path_str)
