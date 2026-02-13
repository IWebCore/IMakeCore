#pragma once

#include "core/util/IHeaderUtil.h"
#include "core/util/IMetaUtil.h"
#include "core/unit/ISoloUnit.h"
#include "core/task/ITaskManage.h"
#include "core/task/default/IStartupTaskCatagory.h"
#include "core/task/unit/ITaskWareUnit.h"

$PackageWebCoreBegin

template<typename T, bool enabled=true>
class IStartupTaskInterface : public ITaskWareUnit<T, IStartupTaskCatagory, enabled>, public ISoloUnit<T>
{
public:
    IStartupTaskInterface() = default;

public:
    virtual double $order() const override;
};

template<typename T, bool enabled>
double IStartupTaskInterface<T, enabled>::$order() const
{
    return 50;
}

$PackageWebCoreEnd
