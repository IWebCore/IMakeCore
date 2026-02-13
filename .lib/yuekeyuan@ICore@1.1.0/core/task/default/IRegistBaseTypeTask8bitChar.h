#pragma once

#include "core/util/IPackageUtil.h"
#include "core/task/unit/ITaskInstantUnit.h"

$PackageWebCoreBegin

class IRegistBaseTypeTask8bitChar : public ITaskInstantUnit<IRegistBaseTypeTask8bitChar, false>
{
public:
    IRegistBaseTypeTask8bitChar();

public:
    virtual void $task() final;
};

$PackageWebCoreEnd
