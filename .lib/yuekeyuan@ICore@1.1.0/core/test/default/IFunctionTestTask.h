#pragma once

#include "core/test/ITestTaskInterface.h"


$PackageWebCoreBegin

class IFunctionTestTask : public ITestTaskInterface<IFunctionTestTask>
{
public:
    IFunctionTestTask() = default;

public:
    virtual double $order() const final;
    virtual void $task() final;
};

$PackageWebCoreEnd
