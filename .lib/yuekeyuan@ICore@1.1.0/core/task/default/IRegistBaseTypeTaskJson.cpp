#include "IRegistBaseTypeTaskJson.h"
#include "core/unit/IRegisterMetaTypeUnit.h"

$PackageWebCoreBegin

IRegistBaseTypeTaskJson::IRegistBaseTypeTaskJson()
{

}

void IRegistBaseTypeTaskJson::$task()
{
    IRegisterMetaTypeUnit<IJson>::registType();
}

$PackageWebCoreEnd
