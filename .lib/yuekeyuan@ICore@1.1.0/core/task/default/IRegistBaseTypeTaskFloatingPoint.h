#pragma once

#include "core/util/IPackageUtil.h"
#include "core/task/unit/ITaskInstantUnit.h"

$PackageWebCoreBegin

class IRegistBaseTypeTaskFloatingPoint : public ITaskInstantUnit<IRegistBaseTypeTaskFloatingPoint, true>
{
public:
    IRegistBaseTypeTaskFloatingPoint();

public:
    virtual void $task() final;
};

$PackageWebCoreEnd
