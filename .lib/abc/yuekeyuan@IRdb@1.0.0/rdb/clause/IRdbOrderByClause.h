#pragma once

#include "core/util/IHeaderUtil.h"
#include "rdb/clause/IRdbClause.h"

$PackageWebCoreBegin

struct IRdbOrderByClause : public IRdbClause
{
public:
    IRdbOrderByClause() = default;
    IRdbOrderByClause(const QString& field, bool isAscending=true);

public:
    QString m_field;
    bool m_isAscending{true};
};

namespace IRdb
{
    IRdbOrderByClause orderByAsc(const QString& field);
    IRdbOrderByClause orderByDesc(const QString& field);
}

$PackageWebCoreEnd
