#pragma once

#include "core/util/IHeaderUtil.h"
#include "rdb/clause/IRdbCondition.h"
#include "rdb/clause/IRdbWhereClause.h"
#include "rdb/clause/IRdbOrderByClause.h"
#include "rdb/clause/IRdbGroupByClause.h"
#include "rdb/clause/IRdbHavingClause.h"
#include "rdb/clause/IRdbLimitClause.h"

$PackageWebCoreBegin

class IRdbConditionImpl
{
public:
    bool m_isChild{false};
    bool m_isAnd{true};
    bool m_isNot{false};
    std::list<IRdbCondition> m_subConditions;

    std::map<int, IRdbWhereClause> m_wheres;
    std::map<int, IRdbCondition> m_conditions;
    std::list<IRdbOrderByClause> m_orderBys;
    std::list<IRdbGroupByClause> m_groupBys;
    std::list<IRdbHavingClause> m_havings;
    IRdbLimitClause m_limit;
};

$PackageWebCoreEnd
