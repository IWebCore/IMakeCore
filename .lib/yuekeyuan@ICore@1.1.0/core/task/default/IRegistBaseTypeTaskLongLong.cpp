#include "IRegistBaseTypeTaskLongLong.h"
#include "core/unit/IRegisterMetaTypeUnit.h"

$PackageWebCoreBegin

IRegistBaseTypeTaskLongLong::IRegistBaseTypeTaskLongLong()
{

}

void IRegistBaseTypeTaskLongLong::$task()
{
    IRegisterMetaTypeUnit<long long>::registType();
    IRegisterMetaTypeUnit<unsigned long long>::registType();
}

$PackageWebCoreEnd
