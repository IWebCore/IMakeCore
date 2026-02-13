#include "IUnitTestTask.h"
#include "core/test/ITestManage.h"
#include "core/config/IContextImport.h"

$PackageWebCoreBegin

double IUnitTestTask::$order() const
{
    return 1;
}

void IUnitTestTask::$task()
{
    $ContextBool enabled("/test/unitTest/enabled", false);
    if(! (*enabled)){
        return;
    }
    if(!ITestManage::instance().hasTests("unitTest")){
        return;
    }
    qDebug() << "START UNIT TEST";
    ITestManage::instance().invokeTests("unitTest");
}

$PackageWebCoreEnd
