#include "IRdbHavingClause.h"

$PackageWebCoreBegin

IRdbHavingClause::IRdbHavingClause(const QString &sql, IRdb::Relation relation)
    : m_havingSql(sql), m_relation(relation)
{
}

IRdbHavingClause IRdb::having(const QString &sql, IRdb::Relation relation)
{
    return IRdbHavingClause (sql, relation);
}

$PackageWebCoreEnd
