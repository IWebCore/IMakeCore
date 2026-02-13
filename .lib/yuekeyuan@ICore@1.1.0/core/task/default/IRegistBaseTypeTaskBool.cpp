#include "IRegistBaseTypeTaskBool.h"
#include "core/unit/IRegisterMetaTypeUnit.h"

$PackageWebCoreBegin

IRegistBaseTypeTaskBool::IRegistBaseTypeTaskBool()
{

}

void IRegistBaseTypeTaskBool::$task()
{
    IRegisterMetaTypeUnit<bool>::registType();
}

$PackageWebCoreEnd
