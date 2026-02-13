#pragma once

#include "core/util/IHeaderUtil.h"
#include "core/unit/ISoloUnit.h"
#include "core/task/unit/ITaskWareUnit.h"
#include "http/IHttpTaskCatagory.h"
#include "INodyResolverWare.h"
#include "INodyManage.h"

$PackageWebCoreBegin

template<typename T, bool enabled=true>
class INodyResolverInterface : public INodyResolverWare,
    public ITaskWareUnit<T, IHttpTaskCatagory, enabled>, public ISoloUnit<T>
{
public:
    INodyResolverInterface() = default;

public:
    virtual bool isValid() const;
    virtual void $task() override;
};

template<typename T, bool enabled>
bool INodyResolverInterface<T, enabled>::isValid() const
{
    return true;
}

template<typename T, bool enabled>
void INodyResolverInterface<T, enabled>::$task()
{
    if(isValid()){
        INodyManage::instance().registNodyResolverWare(&ISolo<T>());
    }
}

$PackageWebCoreEnd
