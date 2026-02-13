#pragma once

#include "core/util/IPackageUtil.h"
#include "core/task/unit/ITaskInstantUnit.h"

$PackageWebCoreBegin

class IRegistBaseTypeTaskJson : public ITaskInstantUnit<IRegistBaseTypeTaskJson, true>
{
public:
    IRegistBaseTypeTaskJson();

public:
    virtual void $task() final;
};

$PackageWebCoreEnd
