#include "IRegistBaseTypeTaskShort.h"
#include "core/unit/IRegisterMetaTypeUnit.h"

$PackageWebCoreBegin

IRegistBaseTypeTaskShort::IRegistBaseTypeTaskShort()
{

}

void IRegistBaseTypeTaskShort::$task()
{
    IRegisterMetaTypeUnit<short>::registType();
    IRegisterMetaTypeUnit<unsigned short>::registType();
}

$PackageWebCoreEnd
