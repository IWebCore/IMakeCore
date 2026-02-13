#pragma once

#include "core/util/IHeaderUtil.h"
#include "core/unit/ISoloUnit.h"

$PackageWebCoreBegin

class INodyResolverWare;
class INodyManage : public ISoloUnit<INodyManage>
{
public:
    INodyManage() = default;

public:
    void registNodyResolverWare(INodyResolverWare*);

public:
    bool canParse(const IString& path);
    std::string parse(const IString& path, const IJson& object);

private:
    std::vector<INodyResolverWare*> m_wares;
};

$PackageWebCoreEnd
