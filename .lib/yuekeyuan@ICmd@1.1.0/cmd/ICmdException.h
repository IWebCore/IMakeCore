#pragma once

#include "core/base/IException.h"

$PackageWebCoreBegin

class ICmdException : public IException
{
public:
    ICmdException() = default;
    using IException::IException;
};

$PackageWebCoreEnd
