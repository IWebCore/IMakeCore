#pragma once

#include "core/unit/ISoloUnit.h"
#include "core/task/ITaskManage.h"
#include "core/task/ITaskCatagory.h"
#include "core/task/unit/ITaskCatagoryUnit.h"

$PackageWebCoreBegin

template<typename T, bool enabled=true>
class ITaskCatagoryInterface : public ITaskCatagoryUnit<T, enabled>, public ISoloUnit<T>
{
public:
    ITaskCatagoryInterface() = default;

public:
    virtual const std::string& $catagory() const final;
};

template<typename T, bool enabled>
const std::string& ITaskCatagoryInterface<T, enabled>::$catagory() const
{
    static const std::string name = IMetaUtil::getBareTypeName<T>();
    return name;
}

$PackageWebCoreEnd
