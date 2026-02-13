#pragma once

#include "core/test/ITestTaskInterface.h"

$PackageWebCoreBegin

class IUnitTestTask : public ITestTaskInterface<IUnitTestTask>
{
public:
    IUnitTestTask() = default;

public:
    virtual double $order() const final;
    virtual void $task() final;
};

$PackageWebCoreEnd
