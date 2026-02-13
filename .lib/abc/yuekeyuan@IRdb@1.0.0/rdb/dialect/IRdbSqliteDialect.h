#pragma once

#include "core/util/IHeaderUtil.h"
#include "rdb/dialect/IRdbDialectInterface.h"

$PackageWebCoreBegin

class IRdbTableInfo;
class IRdbSqliteDialect : public IRdbDialectInterface<IRdbSqliteDialect>
{
public:
    IRdbSqliteDialect() = default;
    virtual QString databaseType() const final;

public:
    virtual QString dropTableSql(const IRdbTableInfo &info) const;


public:
    virtual QString getSqlType(const IRdbTableInfo& info, int index) const;
};

$PackageWebCoreEnd
