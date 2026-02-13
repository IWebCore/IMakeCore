#pragma once

#include "core/util/IHeaderUtil.h"
#include "core/task/ITaskCatagoryInterface.h"

$PackageWebCoreBegin

class ITestCatagory : public ITaskCatagoryInterface<ITestCatagory>
{
public:
    virtual double $order() const final;
};

inline double ITestCatagory::$order() const
{
    return 99;
}

$PackageWebCoreEnd
