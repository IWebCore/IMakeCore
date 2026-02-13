#include "IRdbLimitClause.h"

$PackageWebCoreBegin

IRdbLimitClause::IRdbLimitClause(signed long long limit, signed long long offset)
    : m_limit(limit), m_offset(offset)
{
}

IRdbLimitClause IRdb::limit(signed long long limit, signed long long offset)
{
    return IRdbLimitClause(limit, offset);
}

$PackageWebCoreEnd
