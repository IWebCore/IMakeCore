#pragma once

#include "core/util/IHeaderUtil.h"

$PackageWebCoreBegin

struct IRdbGroupByClause
{
public:
    IRdbGroupByClause() = default;
    IRdbGroupByClause(const QString& field);

public:
    QString m_field;
};

namespace IRdb
{
    IRdbGroupByClause groupBy(const QString& field);
}

$PackageWebCoreEnd
