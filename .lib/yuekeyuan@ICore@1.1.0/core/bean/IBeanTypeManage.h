#pragma once

#include "core/util/IHeaderUtil.h"
#include "core/unit/ISoloUnit.h"
#include <unordered_set>

$PackageWebCoreBegin

class IBeanTypeManage : public ISoloUnit<IBeanTypeManage>
{
public:
    using FromJsonFun = std::function<bool(void*ptr, const IJson&)>;
    using ToJsonFun =  std::function<IJson(void* ptr)>;
public:
    IBeanTypeManage() = default;

public:
    void registBeanId(int id);
    void registBeanFromJsonFun(int id, FromJsonFun);
    void registBeanToJsonFun(int id, ToJsonFun);
    FromJsonFun getBeanFromJsonFun(int id);
    ToJsonFun getBeanToJsonFun(int id);
    bool isBeanIdExist(int id) const;

private:
    std::unordered_set<int> m_beanIds;
    QMap<int, FromJsonFun> m_beanFromJsonFunMap;
    QMap<int, ToJsonFun> m_beanToJsonFunMap;
};

$PackageWebCoreEnd

