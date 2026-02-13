#include "IBeanTypeManage.h"
#include "core/bean/IBeanAbort.h"

$PackageWebCoreBegin

void IBeanTypeManage::registBeanId(int id)
{
    m_beanIds.insert(id);
}

void IBeanTypeManage::registBeanFromJsonFun(int id, IBeanTypeManage::FromJsonFun assign)
{
    m_beanFromJsonFunMap[id] = assign;
}

void IBeanTypeManage::registBeanToJsonFun(int id, IBeanTypeManage::ToJsonFun fetch)
{
    m_beanToJsonFunMap[id] = fetch;
}

IBeanTypeManage::FromJsonFun IBeanTypeManage::getBeanFromJsonFun(int id)
{
    if(m_beanFromJsonFunMap.contains(id)){
        return m_beanFromJsonFunMap[id];
    }

    QString tip = QString("type id:").append(QString::number(id)).append(" typename").append(IMetaUtil::typeName(id));
    IBeanAbort::abortTypeNotRegisteredForJsonConvertion(tip, $ISourceLocation);
    return nullptr;
}

IBeanTypeManage::ToJsonFun IBeanTypeManage::getBeanToJsonFun(int id)
{
    if(m_beanToJsonFunMap.contains(id)){
        return m_beanToJsonFunMap[id];
    }
    QString tip = QString("type id:").append(QString::number(id)).append(" typename").append(IMetaUtil::typeName(id));
    IBeanAbort::abortTypeNotRegisteredForJsonConvertion(tip, $ISourceLocation);
    return nullptr;
}

bool IBeanTypeManage::isBeanIdExist(int id) const
{
    return m_beanIds.find(id) != m_beanIds.end();
}

$PackageWebCoreEnd
