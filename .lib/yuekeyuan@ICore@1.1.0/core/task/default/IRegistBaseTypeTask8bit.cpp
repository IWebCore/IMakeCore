#include "IRegistBaseTypeTask8bit.h"
#include "core/unit/IRegisterMetaTypeUnit.h"

$PackageWebCoreBegin

IRegistBaseTypeTask8bit::IRegistBaseTypeTask8bit()
{

}

void IRegistBaseTypeTask8bit::$task()
{
    IRegisterMetaTypeUnit<uchar>::registType();
    IRegisterMetaTypeUnit<signed char>::registType();
}

$PackageWebCoreEnd
