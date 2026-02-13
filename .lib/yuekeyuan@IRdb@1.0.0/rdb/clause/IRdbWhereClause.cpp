#include "IRdbWhereClause.h"

$PackageWebCoreBegin

IRdbWhereClause IRdb::Not(IRdbWhereClause && clause)
{
    clause.m_isNot = !clause.m_isNot;
    return std::move(clause);
}

IRdbWhereClause &IRdb::Not(IRdbWhereClause & clause)
{
    clause.m_isNot = !clause.m_isNot;
    return clause;
}

IRdbWhereClause IRdb::where(const QString &sql, Relation relation)
{
    IRdbWhereClause clause;

    clause.m_type = IRdbWhereClause::Type::Where;
    clause.m_isAnd = !(relation & 0b01);
    clause.m_isNot = !(relation & 0b10);
    clause.m_arguments << sql;

    return clause;
}

IRdbWhereClause IRdb::whereLike(const QString &field, const QString &argument, Relation relation)
{
    IRdbWhereClause clause;

    clause.m_type = IRdbWhereClause::Type::WhereLike;
    clause.m_isAnd = !(relation & 0b01);
    clause.m_isNot = !(relation & 0b10);
    clause.m_field = field;
    clause.m_arguments << argument;

    return clause;
}

IRdbWhereClause IRdb::whereNotLike(const QString &field, const QString &argument, Relation relation)
{
    IRdbWhereClause clause;

    clause.m_type = IRdbWhereClause::Type::whereNotLike;
    clause.m_isAnd = !(relation & 0b01);
    clause.m_isNot = !(relation & 0b10);
    clause.m_field = field;
    clause.m_arguments << argument;

    return clause;
}

IRdbWhereClause IRdb::whereEndWith(const QString &field, const QString &argument, Relation relation)
{
    IRdbWhereClause clause;

    clause.m_type = IRdbWhereClause::Type::WhereEndWith;
    clause.m_isAnd = !(relation & 0b01);
    clause.m_isNot = !(relation & 0b10);
    clause.m_field = field;
    clause.m_arguments << argument;

    return clause;
}

IRdbWhereClause IRdb::whereStartWith(const QString &field, const QString &argument, Relation relation)
{
    IRdbWhereClause clause;

    clause.m_type = IRdbWhereClause::Type::WhereStartWith;
    clause.m_isAnd = !(relation & 0b01);
    clause.m_isNot = !(relation & 0b10);
    clause.m_field = field;
    clause.m_arguments << argument;

    return clause;
}

IRdbWhereClause IRdb::whereBetween(const QString &field, const QVariant &lower, const QVariant &upper, Relation relation)
{
    IRdbWhereClause clause;

    clause.m_type = IRdbWhereClause::Type::WhereBetween;
    clause.m_isAnd = !(relation & 0b01);
    clause.m_isNot = !(relation & 0b10);
    clause.m_field = field;
    clause.m_variants << lower << upper;

    return clause;
}

IRdbWhereClause IRdb::whereIn(const QString &field, const QVariantList & variants, Relation relation)
{
    IRdbWhereClause clause;

    clause.m_type = IRdbWhereClause::Type::WhereIn;
    clause.m_isAnd = !(relation & 0b01);
    clause.m_isNot = !(relation & 0b10);
    clause.m_field = field;
    clause.m_variants = variants;

    return clause;
}

IRdbWhereClause IRdb::whereEqual(const QString &field, const QVariant &argument, Relation relation)
{
    IRdbWhereClause clause;

    clause.m_type = IRdbWhereClause::Type::WhereEqual;
    clause.m_isAnd = !(relation & 0b01);
    clause.m_isNot = !(relation & 0b10);
    clause.m_field = field;
    clause.m_variants << argument;

    return clause;
}

IRdbWhereClause IRdb::whereNotEqual(const QString &field, const QVariant &argument, Relation relation)
{
    IRdbWhereClause clause;

    clause.m_type = IRdbWhereClause::Type::WhereNotEqual;
    clause.m_isAnd = !(relation & 0b01);
    clause.m_isNot = !(relation & 0b10);
    clause.m_field = field;
    clause.m_variants << argument;

    return clause;
}

IRdbWhereClause IRdb::whereGreaterThan(const QString &field, const QVariant &argument, Relation relation)
{
    IRdbWhereClause clause;

    clause.m_type = IRdbWhereClause::Type::WhereGreaterThan;
    clause.m_isAnd = !(relation & 0b01);
    clause.m_isNot = !(relation & 0b10);
    clause.m_field = field;
    clause.m_variants << argument;

    return clause;
}

IRdbWhereClause IRdb::whereGreaterEqual(const QString &field, const QVariant &argument, Relation relation)
{
    IRdbWhereClause clause;

    clause.m_type = IRdbWhereClause::Type::WhereGreaterEqual;
    clause.m_isAnd = !(relation & 0b01);
    clause.m_isNot = !(relation & 0b10);
    clause.m_field = field;
    clause.m_variants << argument;

    return clause;
}

IRdbWhereClause IRdb::whereLessThan(const QString &field, const QVariant &argument, Relation relation)
{
    IRdbWhereClause clause;

    clause.m_type = IRdbWhereClause::Type::WhereLessThan;
    clause.m_isAnd = !(relation & 0b01);
    clause.m_isNot = !(relation & 0b10);
    clause.m_field = field;
    clause.m_variants << argument;

    return clause;
}

IRdbWhereClause IRdb::whereLessEqual(const QString &field, const QVariant &argument, Relation relation)
{
    IRdbWhereClause clause;

    clause.m_type = IRdbWhereClause::Type::WhereLessEqual;
    clause.m_isAnd = !(relation & 0b01);
    clause.m_isNot = !(relation & 0b10);
    clause.m_field = field;
    clause.m_variants << argument;

    return clause;
}

IRdbWhereClause IRdb::whereIsNull(const QString &field, IRdb::Relation relation)
{
    IRdbWhereClause clause;
    clause.m_type = IRdbWhereClause::Type::WhereIsNull;
    clause.m_field = field;
    clause.m_isAnd = !(relation & 0b01);
    clause.m_isNot = !(relation & 0b10);
    return clause;
}

IRdbWhereClause IRdb::whereIsNotNull(const QString &field, IRdb::Relation relation)
{
    IRdbWhereClause clause;
    clause.m_type = IRdbWhereClause::Type::WhereIsNotNull;
    clause.m_field = field;
    clause.m_isAnd = !(relation & 0b01);
    clause.m_isNot = !(relation & 0b10);
    return clause;
}

IRdbWhereClause IRdb::whereTrue(Relation relation)
{
    IRdbWhereClause clause;
    clause.m_type = IRdbWhereClause::Type::WhereTrue;
    clause.m_isAnd = !(relation & 0b01);
    clause.m_isNot = !(relation & 0b10);
    return clause;
}

IRdbWhereClause IRdb::whereFalse(Relation relation)
{
    IRdbWhereClause clause;
    clause.m_type = IRdbWhereClause::Type::WhereFalse;
    clause.m_isAnd = !(relation & 0b01);
    clause.m_isNot = !(relation & 0b10);
    return clause;
}

$PackageWebCoreEnd
