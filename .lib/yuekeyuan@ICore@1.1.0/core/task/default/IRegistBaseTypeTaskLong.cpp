#include "IRegistBaseTypeTaskLong.h"
#include "core/unit/IRegisterMetaTypeUnit.h"

$PackageWebCoreBegin

IRegistBaseTypeTaskLong::IRegistBaseTypeTaskLong()
{

}

void IRegistBaseTypeTaskLong::$task()
{
    IRegisterMetaTypeUnit<long>::registType();
    IRegisterMetaTypeUnit<unsigned long>::registType();
}

$PackageWebCoreEnd
