#pragma once

#include "core/util/IHeaderUtil.h"
#include "IApplicationAnnomacro.h"

$PackageWebCoreBegin

class IApplication
{
public:
    IApplication(int argc, char** argv, const QString& type = {});
    ~IApplication();

public:
    int exec();
};

$PackageWebCoreEnd
