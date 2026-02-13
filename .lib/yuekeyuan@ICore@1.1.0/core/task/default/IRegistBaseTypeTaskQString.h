#pragma once

#include "core/util/IPackageUtil.h"
#include "core/task/unit/ITaskInstantUnit.h"

$PackageWebCoreBegin

class IRegistBaseTypeTaskQString : public ITaskInstantUnit<IRegistBaseTypeTaskQString, true>
{
public:
    IRegistBaseTypeTaskQString();

public:
    virtual void $task() final;
};

$PackageWebCoreEnd
