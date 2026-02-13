#pragma once

#include "core/util/IPackageUtil.h"
#include "core/task/unit/ITaskInstantUnit.h"

$PackageWebCoreBegin

class IRegistBaseTypeTask8bit : public ITaskInstantUnit<IRegistBaseTypeTask8bit, false>
{
public:
    IRegistBaseTypeTask8bit();

public:
    virtual void $task() final;
};

$PackageWebCoreEnd
