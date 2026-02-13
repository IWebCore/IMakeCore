#pragma once

#include "core/util/IHeaderUtil.h"
#include "core/config/IContextTaskInterface.h"
#include "core/config/IConfigPreProcessor.h"

$PackageWebCoreBegin

class IContextLoadSystemVariableTask : public IContextTaskInterface<IContextLoadSystemVariableTask, true>
{
public:
    IContextLoadSystemVariableTask();
public:
    virtual IJson config() final;
};

$PackageWebCoreEnd

