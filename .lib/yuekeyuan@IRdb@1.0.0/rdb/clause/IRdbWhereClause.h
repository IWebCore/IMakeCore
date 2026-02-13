#pragma once

#include "core/util/IHeaderUtil.h"
#include "rdb/clause/IRdbClause.h"

$PackageWebCoreBegin

struct IRdbWhereClause : public IRdbClause
{
public:
    enum class Type
    {
        Where,  // sql only

        WhereLike,
        whereNotLike,
        WhereEndWith,
        WhereStartWith,

        WhereBetween,
        WhereIn,

        WhereEqual,
        WhereNotEqual,
        WhereGreaterThan,
        WhereGreaterEqual,
        WhereLessThan,
        WhereLessEqual,

        WhereIsNull,
        WhereIsNotNull,

        WhereTrue,
        WhereFalse,
    };

public:
    IRdbWhereClause() = default;

public:
    Type m_type;
    bool m_isAnd{true};
    bool m_isNot{false};
    QString m_field;
    QStringList m_arguments;
    QVariantList m_variants;
};

namespace IRdb
{
    IRdbWhereClause Not(IRdbWhereClause &&);
    IRdbWhereClause& Not(IRdbWhereClause&);

    IRdbWhereClause where(const QString& sql, Relation = Relation::And);

    IRdbWhereClause whereLike(const QString& field, const QString& argument, Relation = Relation::And);
    IRdbWhereClause whereNotLike(const QString& field, const QString& argument, Relation = Relation::And);
    IRdbWhereClause whereEndWith(const QString& field, const QString& argument, Relation = Relation::And);
    IRdbWhereClause whereStartWith(const QString& field, const QString& argument, Relation = Relation::And);

    IRdbWhereClause whereBetween(const QString& field, const QVariant& lower, const QVariant& upper, Relation = Relation::And);
    IRdbWhereClause whereIn(const QString& field, const QVariantList&, Relation = Relation::And);

    IRdbWhereClause whereEqual(const QString& field, const QVariant& argument, Relation = Relation::And);
    IRdbWhereClause whereNotEqual(const QString& field, const QVariant& argument, Relation = Relation::And);
    IRdbWhereClause whereGreaterThan(const QString& field, const QVariant& argument, Relation = Relation::And);
    IRdbWhereClause whereGreaterEqual(const QString& field, const QVariant& argument, Relation = Relation::And);
    IRdbWhereClause whereLessThan(const QString& field, const QVariant& argument, Relation = Relation::And);
    IRdbWhereClause whereLessEqual(const QString& field, const QVariant& argument, Relation = Relation::And);

    IRdbWhereClause whereIsNull(const QString& field, Relation = Relation::And);
    IRdbWhereClause whereIsNotNull(const QString& field, Relation = Relation::And);

    IRdbWhereClause whereTrue(Relation = Relation::And);
    IRdbWhereClause whereFalse(Relation = Relation::And);
}

$PackageWebCoreEnd
