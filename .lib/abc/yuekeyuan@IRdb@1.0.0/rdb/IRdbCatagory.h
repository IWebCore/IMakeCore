#pragma once

#include "core/util/IHeaderUtil.h"
#include "core/task/ITaskCatagoryInterface.h"

$PackageWebCoreBegin

struct IRdbCatagory : public ITaskCatagoryInterface<IRdbCatagory>
{
public:
    virtual double $order() const final;
};

$PackageWebCoreEnd
