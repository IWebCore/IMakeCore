#pragma once

#include "core/util/IHeaderUtil.h"


$PackageWebCoreBegin

struct IRdbWhereClause;
struct IRdbOrderByClause;
struct IRdbGroupByClause;
struct IRdbHavingClause;
struct IRdbLimitClause;

class ISqlQuery;
class IRdbCondition;
class IRdbTableInfo;
class IRdbViewInfo;
class IRdbEntityInfo;
class IRdbDialectWare
{
public:
    IRdbDialectWare() = default;
    virtual ~IRdbDialectWare() = default;

public:
    virtual QString databaseType() const = 0;

public:
    virtual QString createTableSql(const IRdbTableInfo& info) const; 
    virtual QString dropTableSql(const IRdbTableInfo& info) const;
    virtual QString dropViewSql(const IRdbViewInfo& info) const;

    QString countSql(const IRdbEntityInfo& info) const;
    QString countSql(const IRdbEntityInfo& info, const IRdbCondition& condition) const;

    virtual void insert(ISqlQuery &query, const IRdbTableInfo &info, void *) const;
    virtual void insert(ISqlQuery& query, const IRdbTableInfo& info, const void*) const;

    void insertAll(ISqlQuery& query, const IRdbTableInfo& info, QVector<const void*>) const;


    QString findOneSql(const IRdbEntityInfo& info, const IRdbCondition& condition) const;
    QString findAllSql(const IRdbEntityInfo& info) const;
    QString findAllSql(const IRdbEntityInfo &info, const IRdbCondition& condition) const;
    QString findColumnSql(const IRdbEntityInfo& info, const QStringList& columns) const;
    QString findColumnSql(const IRdbEntityInfo& info, const QStringList& columns, const IRdbCondition&) const;

    QString existSql(const IRdbEntityInfo&, const IRdbCondition&) const;

    QString updateOne(const IRdbTableInfo& info, const QStringList& columns) const;
    QString updateWhere(const IRdbTableInfo& info, const QVariantMap& map, const IRdbCondition& condition) const;

    QString deleteTableSql(const IRdbEntityInfo& info) const;
    QString deleteTableSql(const IRdbEntityInfo& info, const IRdbCondition& condition) const;
    QString truncateTableSql(const IRdbEntityInfo& info) const;

    virtual QString getSqlType(const IRdbTableInfo& info, int index) const = 0;

public:
    QString conditionToSql(const IRdbCondition&) const;

protected:
    QString toWhereSql(const IRdbCondition&) const;
    QString toOrderBySql(const IRdbCondition&) const;
    QString toGroupBySql(const IRdbCondition&) const;
    QString toHavingSql(const IRdbCondition&) const;
    QString toLimitSql(const IRdbCondition&) const;

    QString fromWhereClause(const IRdbWhereClause&) const;
    QString fromWhereClauseImpl(const IRdbWhereClause&) const;
    QString fromOrderByClause(const IRdbOrderByClause&) const;
    virtual QString fromLimitClause(const IRdbLimitClause&) const;
    QString fromGroupByClause(const IRdbGroupByClause&) const;
    QString fromHavingClause(const IRdbHavingClause&) const;
    virtual QString createSqlCommonKeyClause(const IRdbTableInfo& info, int index) const;

public:
    virtual void bindParameter(QSqlQuery& query, const QString& field, const QVariant& value) const;
    virtual QString quoteName(const QString& name) const;

protected:
    static QString getVividName(const QString&);
};

$PackageWebCoreEnd
