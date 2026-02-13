#pragma once

#include "core/util/IHeaderUtil.h"
#include "core/task/default/IStartupTaskInterface.h"

$PackageWebCoreBegin

class IBannerTask : public IStartupTaskInterface<IBannerTask>
{
private:
    virtual void $task() override final;
    virtual double $order() const override final;
};

$PackageWebCoreEnd
