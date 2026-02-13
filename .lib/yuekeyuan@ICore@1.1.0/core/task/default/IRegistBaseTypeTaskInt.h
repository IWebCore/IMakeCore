#pragma once

#include "core/util/IPackageUtil.h"
#include "core/task/unit/ITaskInstantUnit.h"

$PackageWebCoreBegin

class IRegistBaseTypeTaskInt : public ITaskInstantUnit<IRegistBaseTypeTaskInt, true>
{
public:
    IRegistBaseTypeTaskInt();

public:
    virtual void $task() final;
};

$PackageWebCoreEnd
