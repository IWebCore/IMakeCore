#pragma once

#include "core/util/IHeaderUtil.h"
#include "core/unit/ISoloUnit.h"
#include "core/base/IResult.h"

$PackageWebCoreBegin

class IConfigManageInterface
{
public:
    void addConfig(const IJson& value, const std::string& path="");

    IJson getConfig(const QString& path);
    IJson getConfig(const std::string& path);

protected:
    IJson m_configs = IJson::object();
};

$PackageWebCoreEnd
