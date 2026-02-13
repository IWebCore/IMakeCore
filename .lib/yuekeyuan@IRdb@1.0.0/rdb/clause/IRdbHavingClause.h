#pragma once

#include "core/util/IHeaderUtil.h"
#include "rdb/clause/IRdbClause.h"

$PackageWebCoreBegin

// NOTE: 这个地方想了一下，不用再扩展，之后有时间再进行扩展。
struct IRdbHavingClause
{
public:
    IRdbHavingClause() = default;
    IRdbHavingClause(const QString& sql, IRdb::Relation relation=IRdb::Relation::And);

public:
    QString m_havingSql;
    IRdb::Relation m_relation;
};

namespace IRdb
{
    IRdbHavingClause having(const QString& sql, Relation = Relation::And);
}

$PackageWebCoreEnd
