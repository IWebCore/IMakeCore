#pragma once

#include "rdb/dialect/IRdbDialectInterface.h"

$PackageWebCoreBegin

class IRdbPostgresDialect : public IRdbDialectInterface<IRdbPostgresDialect>
{
public:
    IRdbPostgresDialect() = default;
    virtual QString databaseType() const final;

public:
    virtual QString getSqlType(const IRdbTableInfo &info, int index) const;
    virtual QString createSqlCommonKeyClause(const IRdbTableInfo &info, int index) const final;
};

$PackageWebCoreEnd
