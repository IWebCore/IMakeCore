#pragma once

#include "core/util/IHeaderUtil.h"
#include "core/unit/ISoloUnit.h"
#include "rdb/dialect/IRdbDialectWare.h"

$PackageWebCoreBegin

template<typename T>
class IRdbDialectInterface : public IRdbDialectWare, public ISoloUnit<T>
{
};

$PackageWebCoreEnd
