#pragma once

#include "rdb/dialect/IRdbMysqlDialect.h"

$PackageWebCoreBegin

class IRdbMariaDbDialect : public IRdbMysqlDialect
{
public:
    IRdbMariaDbDialect() = default;
    virtual QString databaseType() const final;
};

$PackageWebCoreEnd
