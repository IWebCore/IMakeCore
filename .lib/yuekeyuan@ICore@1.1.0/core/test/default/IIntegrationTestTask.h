#pragma once

#include "core/util/IHeaderUtil.h"
#include "core/test/ITestTaskInterface.h"
#include "core/test/ITestManage.h"

$PackageWebCoreBegin

class IIntegrationTestTask : public ITestTaskInterface<IIntegrationTestTask>
{
public:
    IIntegrationTestTask() = default;

public:
    virtual double $order() const final;
    virtual void $task() final;
};

$PackageWebCoreEnd
