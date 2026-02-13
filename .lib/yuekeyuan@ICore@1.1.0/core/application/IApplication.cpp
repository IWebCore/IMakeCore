#include "IApplication.h"
#include "IApplicationManage.h"
#include "iApp.h"

$PackageWebCoreBegin

IApplication::IApplication(int argc, char **argv, const QString &type)
{
    if(iApp){
        qFatal("app already started");
    }

    if(type.isEmpty()){
        if(auto fun = IApplicationManage::instance().getAppFunction("asio"); fun){
            iApp = fun(argc, argv);
        }else if(auto fun = IApplicationManage::instance().getAppFunction("QCore"); fun){
            iApp = fun(argc, argv);
        }
    }else if(auto fun = IApplicationManage::instance().getAppFunction(type); fun){
        iApp = fun(argc, argv);
    }

    if(!iApp){
        qFatal("app function not found");
    }

    ITaskManage::run();
}

IApplication::~IApplication()
{
}

int IApplication::exec()
{
    return iApp->exec();
}

$PackageWebCoreEnd
