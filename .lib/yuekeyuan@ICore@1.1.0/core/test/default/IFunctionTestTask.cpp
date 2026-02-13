#include "IFunctionTestTask.h"
#include "core/test/ITestManage.h"
#include "core/config/IContextImport.h"

$PackageWebCoreBegin

double IFunctionTestTask::$order() const
{
    return 2;
}

void IFunctionTestTask::$task()
{
    $ContextBool enabled("/test/functionTest/enabled", false);
    if(! (*enabled)){
        return;
    }
    if(!ITestManage::instance().hasTests("functionTest")){
        return;
    }

    qDebug() << "START FUNCTION TEST";
    ITestManage::instance().invokeTests("functionTest");
}

$PackageWebCoreEnd
