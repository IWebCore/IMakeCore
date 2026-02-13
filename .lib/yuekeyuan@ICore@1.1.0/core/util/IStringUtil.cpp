#include "IStringUtil.h"

$PackageWebCoreBegin

bool IStringUtil::startsWith(const std::string &str, const std::string &prefix)
{
    return str.compare(0, prefix.size(), prefix) == 0;
}

bool IStringUtil::endsWith(const std::string &str, const std::string &suffix)
{
    if (str.size() < suffix.size()) return false;
    return str.compare(str.size() - suffix.size(), suffix.size(), suffix) == 0;
}

std::string IStringUtil::mid(const std::string &str, size_t start, long long length)
{
    if (start >= str.size()) {
        return "";
    }
    if (length == -1) {
        length = str.size() - start;
    }
    return str.substr(start, length);
}

std::string IStringUtil::left(const std::string &str, long long length)
{
    if (length == -1 || length >= static_cast<long long>(str.size())) {
        return str;
    }
    return str.substr(0, length);
}

std::string IStringUtil::right(const std::string &str, long long length)
{
    if (length == -1 || length >= static_cast<long long>(str.size())) {
        return str;
    }
    return str.substr(str.size() - length, length);
}


$PackageWebCoreEnd
