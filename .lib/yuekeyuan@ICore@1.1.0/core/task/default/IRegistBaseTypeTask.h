#pragma once

#include "core/util/IPackageUtil.h"
#include "core/task/unit/ITaskInstantUnit.h"

$PackageWebCoreBegin

class IRegistBaseTypeTask : public ITaskInstantUnit<IRegistBaseTypeTask, true>
{
public:
    IRegistBaseTypeTask() = default;

public:
    virtual void $task() final;
};

$PackageWebCoreEnd
