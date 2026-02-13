#pragma once

#include "core/util/IHeaderUtil.h"
#include "core/task/ITaskWare.h"
#include "core/task/ITaskManage.h"
#include "core/task/ITaskPreProcessor.h"
#include "core/unit/ISoloUnit.h"

$PackageWebCoreBegin

template<typename T, typename Catagory, bool enabled=true>
class ITaskWareUnit : public ITaskWare
{
    $AsTaskUnit(ITaskWareUnit)
    Q_DISABLE_COPY_MOVE(ITaskWareUnit)
protected:
    ITaskWareUnit() = default;
    virtual ~ITaskWareUnit() = default;

protected:
    virtual const std::string& $name() const final;
    virtual const std::string& $catagory() const final;
};

template<typename T, typename Catagory, bool enabled>
const std::string& ITaskWareUnit<T, Catagory, enabled>::$name() const
{
    static const std::string name = IMetaUtil::getBareTypeName<T>();
    return name;
}

template<typename T, typename Catagory, bool enabled>
const std::string& ITaskWareUnit<T, Catagory, enabled>::$catagory() const
{
    static const std::string name = IMetaUtil::getBareTypeName<Catagory>();
    return name;
}

$UseTaskUnit2(ITaskWareUnit)
{
    if constexpr (enabled){
        static std::once_flag flag;
        std::call_once(flag, [](){
            ITaskManage::instance().addTaskWare(&ISolo<T>());
        });
    }
}

$PackageWebCoreEnd
