#include "IRegistBaseTypeTask8bitChar.h"
#include "core/unit/IRegisterMetaTypeUnit.h"

$PackageWebCoreBegin

IRegistBaseTypeTask8bitChar::IRegistBaseTypeTask8bitChar()
{

}

void IRegistBaseTypeTask8bitChar::$task()
{
    IRegisterMetaTypeUnit<char>::registType();
}

$PackageWebCoreEnd
