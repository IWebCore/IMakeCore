#pragma once

#include "core/util/IHeaderUtil.h"
#include "core/test/ITestManage.h"
#include "core/test/ITestCatagory.h"
#include "core/task/unit/ITaskWareUnit.h"

$PackageWebCoreBegin

template<typename T, bool enabled=true>
class IIntegrationTestInteface :  public ITaskWareUnit<T, ITestCatagory, enabled>, public QObject, public ISoloUnit<T>
{
public:
    IIntegrationTestInteface() = default;

public:
    virtual void $task() final;
    virtual double $order() const final;
};

template<typename T, bool enabled>
void IIntegrationTestInteface<T, enabled>::$task()
{
    if constexpr (enabled){
        ITestManage::instance().addTest("integrationTest", &T::instance());
    }
}

template<typename T, bool enabled>
double IIntegrationTestInteface<T, enabled>::$$order() const
{
    return 2;
}

$PackageWebCoreEnd
