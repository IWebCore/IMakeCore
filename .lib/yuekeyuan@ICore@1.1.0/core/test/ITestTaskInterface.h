#pragma once

#include "core/util/IHeaderUtil.h"
#include "core/task/unit/ITaskWareUnit.h"
#include "core/task/default/IEndupTaskCatagory.h"

$PackageWebCoreBegin

template<typename T, bool enabled=true>
class ITestTaskInterface : public ITaskWareUnit<T, IEndupTaskCatagory, true>
{
public:
    ITestTaskInterface() = default;
public:
    virtual double $order() const override;
};

template<typename T, bool enabled>
double ITestTaskInterface<T, enabled>::$order() const
{
    return 99;
}

$PackageWebCoreEnd
