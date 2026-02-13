#include "IRdbGroupByClause.h"
#include "rdb/clause/IRdbCondition.h"

$PackageWebCoreBegin

IRdbGroupByClause::IRdbGroupByClause(const QString & field)
    : m_field(field)
{
}

IRdbGroupByClause IRdb::groupBy(const QString &field)
{
    return IRdbGroupByClause(field);
}

$PackageWebCoreEnd
