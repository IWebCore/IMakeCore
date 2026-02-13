#pragma once

#include "core/util/IHeaderUtil.h"
#include "core/task/ITaskCatagoryInterface.h"

$PackageWebCoreBegin

struct ICmdCatagory : public ITaskCatagoryInterface<ICmdCatagory>
{
public:
    ICmdCatagory();

public:
    virtual double $order() const final;
};

$PackageWebCoreEnd
