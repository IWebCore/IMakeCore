#pragma once

#include "core/util/IHeaderUtil.h"
#include "core/config/IProfileTaskInterface.h"
#include "core/config/default/ILoadProfileFileUnit.h"

$PackageWebCoreBegin

class IProfileLoadJsonTask : public ITaskWareUnit<IProfileLoadJsonTask, IConfigTaskCatagory, true>, public ILoadProfileFileUnit
{
public:
    IProfileLoadJsonTask();

public:
    virtual double $order() const final;
    IJson config();

private:
    virtual QStringList nameFilters() const final;

private:
    virtual void $task() final;
};

$PackageWebCoreEnd
