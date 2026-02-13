#pragma once

#include "core/unit/ISoloUnit.h"

$PackageWebCoreBegin

class IApplicationWare;
class IApplicationManage : public ISoloUnit<IApplicationManage>
{
public:
    using AppFun = std::function<IApplicationWare*(int, char**)>;

public:
    void registerAppFuns(const QString& name, AppFun);
    AppFun getAppFunction(const QString&);
    
    void regiserCleaner();
    

private:
    QMap<QString, AppFun> m_appFuns;
};

$PackageWebCoreEnd
