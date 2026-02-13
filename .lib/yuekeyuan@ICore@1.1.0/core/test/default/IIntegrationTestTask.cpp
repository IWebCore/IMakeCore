#include "IIntegrationTestTask.h"
#include "core/test/ITestManage.h"
#include "core/config/IContextImport.h"

$PackageWebCoreBegin

double IIntegrationTestTask::$order() const
{
    return 3;
}

void IIntegrationTestTask::$task()
{
    $ContextBool enabled("/test/integrationTest/enabled", false);
    if(! (*enabled)){
        return;
    }
    if(!ITestManage::instance().hasTests("integrationTest")){
        return;
    }
    qDebug() << "START INTEGRATION TEST";
    ITestManage::instance().invokeTests("integrationTest");
}

$PackageWebCoreEnd

