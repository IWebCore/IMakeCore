#include "IRegistBaseTypeTaskFloatingPoint.h"
#include "core/unit/IRegisterMetaTypeUnit.h"

$PackageWebCoreBegin

IRegistBaseTypeTaskFloatingPoint::IRegistBaseTypeTaskFloatingPoint()
{

}

void IRegistBaseTypeTaskFloatingPoint::$task()
{
    IRegisterMetaTypeUnit<float>::registType();
    IRegisterMetaTypeUnit<double>::registType();
}

$PackageWebCoreEnd
