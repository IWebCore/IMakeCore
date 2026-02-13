#pragma once

#include "core/util/IPackageUtil.h"
#include "core/task/unit/ITaskInstantUnit.h"

$PackageWebCoreBegin

class IRegistBaseTypeTaskBool : public ITaskInstantUnit<IRegistBaseTypeTaskBool>
{
public:
    IRegistBaseTypeTaskBool();

public:
    virtual void $task() final;
};

$PackageWebCoreEnd
