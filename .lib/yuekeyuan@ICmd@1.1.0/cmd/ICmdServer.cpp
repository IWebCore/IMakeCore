#include "ICmdServer.h"
#include "core/application/iApp.h"
#include "core/application/IApplicationManage.h"
#include "cmd/ICmdRequest.h"
#include "cmd/ICmdManage.h"
#include "cmd/action/ICmdAction.h"

$PackageWebCoreBegin

ICmdServer::ICmdServer()
{
    m_request = ICmdRequest(iApp->arguments());
}

void ICmdServer::serve()
{
    if(m_request.m_paths.empty()){
        return showGlobalHelp();
    }

    if(m_request.m_isHelp){
        return showHelp();
    }

    auto action = ICmdManage::instance().getAction(m_request);
    if(!action){
        return showGlobalHelp();
    }

    action->execute(m_request);
}

void ICmdServer::showGlobalHelp()
{
    ICmdManage::instance().printHelp();
    exit(1);
}

void ICmdServer::showHelp()
{
    auto action = ICmdManage::instance().getAction(m_request);
    if(action){
        action->printHelp();
        exit(0);
    }else{
        showGlobalHelp();
    }
}

$PackageWebCoreEnd
