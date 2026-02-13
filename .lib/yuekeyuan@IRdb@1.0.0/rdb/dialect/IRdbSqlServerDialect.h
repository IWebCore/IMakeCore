#pragma once

#include "core/util/IHeaderUtil.h"
#include "rdb/dialect/IRdbDialectInterface.h"

$PackageWebCoreBegin

class IRdbTableInfo;
class IRdbSqlServerDialect : public IRdbDialectInterface<IRdbSqlServerDialect>
{
public:
    IRdbSqlServerDialect() = default;
    virtual QString databaseType() const final;

public:
    virtual QString createTableSql(const IRdbTableInfo& info) const override;
    virtual QString dropTableSql(const IRdbTableInfo &info) const override;
    virtual QString getSqlType(const IRdbTableInfo &info, int index) const override;
    virtual QString createSqlCommonKeyClause(const IRdbTableInfo &info, int index) const override;

protected:
    virtual QString fromLimitClause(const IRdbLimitClause&) const override;

public:
    virtual void bindParameter(QSqlQuery& query, const QString& field, const QVariant& value) const override;
    virtual QString quoteName(const QString &name) const final;
};

$PackageWebCoreEnd
