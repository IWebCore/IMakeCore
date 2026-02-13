#pragma once

#include "core/util/IHeaderUtil.h"
#include "core/test/ITestManage.h"
#include "core/test/ITestCatagory.h"
#include "core/task/unit/ITaskWareUnit.h"

$PackageWebCoreBegin

template<typename T, bool enabled=true>
class IFunctionTestInterface :  public ITaskWareUnit<T, ITestCatagory, enabled>, public QObject, public ISoloUnit<T>
{
public:
    IFunctionTestInterface() = default;

public:
    virtual void $task() final;
    virtual double $order() const final;
};

template<typename T, bool enabled>
void IFunctionTestInterface<T, enabled>::$task()
{
    if constexpr (enabled){
        ITestManage::instance().addTest("functionTest", &T::instance());
    }
}

template<typename T, bool enabled>
double IFunctionTestInterface<T, enabled>::$order() const
{
    return 1;
}

$PackageWebCoreEnd
