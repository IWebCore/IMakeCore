#pragma once

#include "core/util/IHeaderUtil.h"
#include "cmd/ICmdRequest.h"

$PackageWebCoreBegin

class ICmdServer
{
public:
    ICmdServer();

public:
    void serve();

private:
    void showGlobalHelp();
    void showHelp();

private:
    ICmdRequest m_request;
};

$PackageWebCoreEnd
