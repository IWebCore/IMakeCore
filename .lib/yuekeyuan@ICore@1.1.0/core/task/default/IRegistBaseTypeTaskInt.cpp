#include "IRegistBaseTypeTaskInt.h"
#include "core/unit/IRegisterMetaTypeUnit.h"

$PackageWebCoreBegin

IRegistBaseTypeTaskInt::IRegistBaseTypeTaskInt()
{

}

void IRegistBaseTypeTaskInt::$task()
{
    IRegisterMetaTypeUnit<int>::registType();
    IRegisterMetaTypeUnit<unsigned int>::registType();
}

$PackageWebCoreEnd
