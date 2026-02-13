#pragma once

#include "core/util/IHeaderUtil.h"
#include "rdb/clause/IRdbWhereClause.h"
#include "rdb/clause/IRdbGroupByClause.h"
#include "rdb/clause/IRdbOrderByClause.h"
#include "rdb/clause/IRdbHavingClause.h"
#include "rdb/clause/IRdbLimitClause.h"

$PackageWebCoreBegin

class ISqlQuery;
class IRdbConditionImpl;
class IRdbCondition
{
public:
    IRdbCondition();
    IRdbCondition(IRdbCondition&&);
    IRdbCondition(const IRdbCondition &);
    IRdbCondition& operator=(IRdbCondition&&);
    IRdbCondition& operator=(const IRdbCondition&);
    ~IRdbCondition();

public:
//    IRdbCondition(const QString& sql); // NOTE: 这个东西之后会集成进去。
    IRdbCondition(IRdbWhereClause&& where);
    IRdbCondition(IRdbOrderByClause&& orderBy);
    IRdbCondition(IRdbGroupByClause&& groupBy);
    IRdbCondition(IRdbLimitClause&& limit);
    IRdbCondition(IRdbHavingClause&& having);

public:
    IRdbCondition& where(const QString& sql, IRdb::Relation = IRdb::Relation::And);
    IRdbCondition& whereLike(const QString& field, const QString& argument, IRdb::Relation = IRdb::Relation::And);
    IRdbCondition& whereNotLike(const QString& field, const QString& argument, IRdb::Relation = IRdb::Relation::And);
    IRdbCondition& whereEndWith(const QString& field, const QString& argument, IRdb::Relation = IRdb::Relation::And);
    IRdbCondition& whereStartWith(const QString& field, const QString& argument, IRdb::Relation = IRdb::Relation::And);
    IRdbCondition& whereBetween(const QString& field, const QVariant& lower, const QVariant& upper, IRdb::Relation = IRdb::Relation::And);
    IRdbCondition& whereIn(const QString& field, const QVariantList&, IRdb::Relation = IRdb::Relation::And);
    IRdbCondition& whereEqual(const QString& field, const QVariant& argument, IRdb::Relation = IRdb::Relation::And);
    IRdbCondition& whereNotEqual(const QString& field, const QVariant& argument, IRdb::Relation = IRdb::Relation::And);
    IRdbCondition& whereGreaterThan(const QString& field, const QVariant& argument, IRdb::Relation = IRdb::Relation::And);
    IRdbCondition& whereGreaterEqual(const QString& field, const QVariant& argument, IRdb::Relation = IRdb::Relation::And);
    IRdbCondition& whereLessThan(const QString& field, const QVariant& argument, IRdb::Relation = IRdb::Relation::And);
    IRdbCondition& whereLessEqual(const QString& field, const QVariant& argument, IRdb::Relation = IRdb::Relation::And);
    IRdbCondition& whereIsNull(const QString& field, IRdb::Relation = IRdb::Relation::And);
    IRdbCondition& whereIsNotNull(const QString& field, IRdb::Relation = IRdb::Relation::And);
    IRdbCondition& whereTrue(IRdb::Relation = IRdb::Relation::And);
    IRdbCondition& whereFalse(IRdb::Relation = IRdb::Relation::And);

//public:
    IRdbCondition& like(const QString& field, const QString& argument, IRdb::Relation = IRdb::Relation::And);
    IRdbCondition& notLike(const QString& field, const QString& argument, IRdb::Relation = IRdb::Relation::And);
    IRdbCondition& endWith(const QString& field, const QString& argument, IRdb::Relation = IRdb::Relation::And);
    IRdbCondition& startWith(const QString& field, const QString& argument, IRdb::Relation = IRdb::Relation::And);
    IRdbCondition& between(const QString& field, const QVariant& lower, const QVariant& upper, IRdb::Relation = IRdb::Relation::And);
    IRdbCondition& in(const QString& field, const QVariantList&, IRdb::Relation = IRdb::Relation::And);
    IRdbCondition& equal(const QString& field, const QVariant& argument, IRdb::Relation = IRdb::Relation::And);
    IRdbCondition& notEqual(const QString& field, const QVariant& argument, IRdb::Relation = IRdb::Relation::And);
    IRdbCondition& greaterThan(const QString& field, const QVariant& argument, IRdb::Relation = IRdb::Relation::And);
    IRdbCondition& greaterEqual(const QString& field, const QVariant& argument, IRdb::Relation = IRdb::Relation::And);
    IRdbCondition& lessThan(const QString& field, const QVariant& argument, IRdb::Relation = IRdb::Relation::And);
    IRdbCondition& lessEqual(const QString& field, const QVariant& argument, IRdb::Relation = IRdb::Relation::And);
    IRdbCondition& isNull(const QString& field, IRdb::Relation = IRdb::Relation::And);
    IRdbCondition& isNotNull(const QString& field, IRdb::Relation = IRdb::Relation::And);
    IRdbCondition& True(IRdb::Relation = IRdb::Relation::And);
    IRdbCondition& False(IRdb::Relation = IRdb::Relation::And);

public:
    IRdbCondition& whereAnd(IRdbCondition condition);
    IRdbCondition& whereAndNot(IRdbCondition condition);
    IRdbCondition& whereOr(IRdbCondition condition);
    IRdbCondition& whereOrNot(IRdbCondition condition);

//public:
    IRdbCondition& And(IRdbCondition condition);
    IRdbCondition& AndNot(IRdbCondition condition);
    IRdbCondition& Or(IRdbCondition condition);
    IRdbCondition& OrNot(IRdbCondition condition);

public:
    IRdbCondition& groupBy(const QString& field);

public:
    IRdbCondition& orderBy(const QString& field, bool m_isAscending = true);
    IRdbCondition& orderByAsc(const QString& field);
    IRdbCondition& orderByDesc(const QString& field);

public:
    IRdbCondition& having(const QString& sql, IRdb::Relation relation = IRdb::Relation::And);

public:
    IRdbCondition& limit(unsigned long long limit, unsigned long long offset=-1);

public:
    IRdbCondition& append(IRdbCondition&& condition);
    IRdbCondition& append(IRdbWhereClause&& where);
    IRdbCondition& append(IRdbOrderByClause&& orderBy);
    IRdbCondition& append(IRdbGroupByClause&& groupBy);
    IRdbCondition& append(IRdbHavingClause&& having);
    IRdbCondition& append(IRdbLimitClause&& limit);

public:
    void bindParameters(ISqlQuery&) const;

public:
    IRdbConditionImpl* m_impl;

private:
    std::atomic_int m_whereIndex {};
};

namespace IRdb
{
    IRdbCondition cond();
}

$PackageWebCoreEnd

// NOTE: this maybe changed latter.
#define $Rdb IRdbCondition()
