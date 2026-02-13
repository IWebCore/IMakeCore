#pragma once

#include "core/util/IPackageUtil.h"
#include "core/task/unit/ITaskInstantUnit.h"

$PackageWebCoreBegin

class IRegistBaseTypeTaskLong : public ITaskInstantUnit<IRegistBaseTypeTaskLong, true>
{
public:
    IRegistBaseTypeTaskLong();

public:
    virtual void $task() final;
};

$PackageWebCoreEnd
