#pragma once

#include "core/util/IPackageUtil.h"
#include "core/task/unit/ITaskInstantUnit.h"

$PackageWebCoreBegin

class IRegistBaseTypeTaskLongLong : public ITaskInstantUnit<IRegistBaseTypeTaskLongLong, true>
{
public:
    IRegistBaseTypeTaskLongLong();

public:
    virtual void $task() final;
};

$PackageWebCoreEnd
