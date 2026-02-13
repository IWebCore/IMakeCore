#pragma once

#include "core/util/IPackageUtil.h"
#include "core/task/ITaskPreProcessor.h"
#include "core/unit/ISoloUnit.h"
#include <mutex>

$PackageWebCoreBegin

template<typename T, bool enabled=true>
class ITaskInstantUnit
{
    $AsTaskUnit(ITaskInstantUnit)
public:
    ITaskInstantUnit() = default;
    virtual ~ITaskInstantUnit() = default;

protected:
    virtual void $task() = 0;
};

$UseTaskUnit(ITaskInstantUnit)
{
    if constexpr (enabled){
        static std::once_flag flag;
        std::call_once(flag, []{
            static_cast<ITaskInstantUnit&>(ISolo<T>()).$task();
        });
    }
}

$PackageWebCoreEnd
