#pragma once

#include "core/util/IHeaderUtil.h"
#include "rdb/dialect/IRdbDialectInterface.h"

$PackageWebCoreBegin

class IRdbMysqlDialect : public IRdbDialectInterface<IRdbMysqlDialect>
{
public:
    IRdbMysqlDialect() = default;
    virtual QString databaseType() const override;

public:
    virtual QString getSqlType(const IRdbTableInfo &info, int index) const override;
    virtual QString createSqlCommonKeyClause(const IRdbTableInfo &info, int index) const final;
    virtual QString quoteName(const QString &name) const override;
};

$PackageWebCoreEnd
