#include "IRdbOrderByClause.h"

$PackageWebCoreBegin

IRdbOrderByClause::IRdbOrderByClause(const QString &field, bool isAscending)
    : m_field(field), m_isAscending(isAscending)
{
}

IRdbOrderByClause IRdb::orderByAsc(const QString &field)
{
    return IRdbOrderByClause(field, true);
}

IRdbOrderByClause IRdb::orderByDesc(const QString &field)
{
    return IRdbOrderByClause(field, false);
}

$PackageWebCoreEnd
