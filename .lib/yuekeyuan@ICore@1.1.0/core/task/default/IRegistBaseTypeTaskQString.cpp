#include "IRegistBaseTypeTaskQString.h"
#include "core/unit/IRegisterMetaTypeUnit.h"

$PackageWebCoreBegin

IRegistBaseTypeTaskQString::IRegistBaseTypeTaskQString()
{

}

void IRegistBaseTypeTaskQString::$task()
{
    IRegisterMetaTypeUnit<QString>::registType();
}

$PackageWebCoreEnd
