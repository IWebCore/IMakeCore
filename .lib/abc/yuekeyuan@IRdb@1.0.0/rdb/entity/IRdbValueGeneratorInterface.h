#pragma once

#include "core/util/IHeaderUtil.h"
#include "core/task/unit/ITaskInstantUnit.h"
#include "rdb/IRdbManage.h"

$PackageWebCoreBegin

template<typename T, bool enabled=true>
class IRdbValueGeneratorInterface : public ITaskInstantUnit<T, enabled>
{
public:
    IRdbValueGeneratorInterface() = default;

public:
    virtual QString name() const = 0;
    virtual QVariant generator() const = 0;

private:
    virtual void $task() final;
};

template<typename T, bool enabled>
void IRdbValueGeneratorInterface<T, enabled>::$task()
{
    if constexpr (enabled){
        IRdbManage::instance().regiterAutoGenerateKeyFunction(name(),
            std::bind(&IRdbValueGeneratorInterface::generator, &ISolo<T>()));
    }
}

$PackageWebCoreEnd
