#pragma once

#include "core/util/IHeaderUtil.h"
#include "rdb/clause/IRdbClause.h"

$PackageWebCoreBegin

struct IRdbLimitClause : public IRdbClause
{
public:
    IRdbLimitClause() = default;
    IRdbLimitClause(signed long long limit, signed long long offset = -1);

public:
    signed long long m_limit{-1};
    signed long long m_offset{-1};   // this means no offset
};

namespace IRdb
{
    IRdbLimitClause limit(signed long long limit, signed long long offset = -1);
}

$PackageWebCoreEnd
