#pragma once

#include "core/util/IHeaderUtil.h"

$PackageWebCoreBegin

struct IGadgetUnit
{
    using StaticMetacallFunction = std::function<void(QObject *, QMetaObject::Call, int, void **)>;
public:
    virtual StaticMetacallFunction staticMetaCallFunction() const = 0;
};

$PackageWebCoreEnd
