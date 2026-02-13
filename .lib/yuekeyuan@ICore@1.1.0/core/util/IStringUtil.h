#pragma once

#include "core/util/IHeaderUtil.h"

$PackageWebCoreBegin

namespace IStringUtil
{
    bool startsWith(const std::string& str, const std::string& prefix);

    bool endsWith(const std::string& str, const std::string& suffix);

    std::string mid(const std::string& str, size_t start, long long length = -1);

    std::string left(const std::string& str, long long length = -1);

    std::string right(const std::string& str, long long length = -1);
}

$PackageWebCoreEnd
