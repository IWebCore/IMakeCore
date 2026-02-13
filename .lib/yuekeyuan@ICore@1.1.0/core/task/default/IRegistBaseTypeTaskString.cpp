#include "IRegisterBaseTypeTaskString.h"
#include "core/unit/IRegisterMetaTypeUnit.h"

$PackageWebCoreBegin

IRegistBaseTypeTaskString::IRegistBaseTypeTaskString()
{

}

void IRegistBaseTypeTaskString::$task()
{
//    IRegisterMetaTypeUnit<IStringView>::registType();

    IRegisterMetaTypeUnit<IString>::registType();
    IRegisterMetaTypeUnit<std::string>::registType();
}

$PackageWebCoreEnd
