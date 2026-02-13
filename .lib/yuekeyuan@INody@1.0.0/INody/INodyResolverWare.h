#pragma once

#include "core/util/IHeaderUtil.h"

$PackageWebCoreBegin

class INodyResolverWare
{
public:
    INodyResolverWare() = default;

public:
    virtual bool match(const IString& path) = 0;
    virtual std::string parse(const IString& path, const IJson& json) = 0;
};

$PackageWebCoreEnd
