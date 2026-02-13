#pragma once

#include "core/util/IPackageUtil.h"
#include "core/task/unit/ITaskInstantUnit.h"

$PackageWebCoreBegin

class IRegistBaseTypeTaskShort : public ITaskInstantUnit<IRegistBaseTypeTaskShort, true>
{
public:
    IRegistBaseTypeTaskShort();

public:
    virtual void $task() final;
};

$PackageWebCoreEnd
