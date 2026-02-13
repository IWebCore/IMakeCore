#include "IApplicationManage.h"

// #include "core/application/IAsioContext.h"
// #include <QCoreApplication>

$PackageWebCoreBegin

void IApplicationManage::registerAppFuns(const QString &name, AppFun fun)
{
    m_appFuns[name] = fun;
}

IApplicationManage::AppFun IApplicationManage::getAppFunction(const QString & name)
{
    if(m_appFuns.contains(name)){
        return m_appFuns[name];
    }
    return nullptr;
}

$PackageWebCoreEnd
