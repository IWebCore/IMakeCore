#include "IRdbDialectWare.h"

#include "core/util/IMetaUtil.h"
#include "rdb/IRdbAbort.h"
#include "rdb/IRdbManage.h"
#include "rdb/ISqlQuery.h"
#include "rdb/IRdbUtil.h"
#include "rdb/clause/IRdbCondition.h"
#include "rdb/clause/IRdbWhereClause.h"
#include "rdb/clause/IRdbGroupByClause.h"
#include "rdb/clause/IRdbOrderByClause.h"
#include "rdb/clause/IRdbHavingClause.h"
#include "rdb/clause/IRdbLimitClause.h"
#include "rdb/clause/impl/IRdbConditionImpl.h"
#include "rdb/entity/IRdbTableInfo.h"
#include "rdb/entity/IRdbViewInfo.h"
#include "rdb/entity/IRdbEntityInfo.h"

$PackageWebCoreBegin

QString IRdbDialectWare::createTableSql(const IRdbTableInfo &info) const
{
    QStringList fields;
    for (auto index = 0; index < info.m_fields.length(); index++) {
        fields.append(createSqlCommonKeyClause(info, index));
    }

    return QString("CREATE TABLE IF NOT EXISTS ")
            .append(quoteName(info.m_entityName))
            .append(" (").append(fields.join(", ") + ')');
}

QString IRdbDialectWare::dropTableSql(const IRdbTableInfo &info) const
{
    return "DROP TABLE IF EXISTS " + quoteName(info.m_entityName) + " CASCADE";
}

QString IRdbDialectWare::dropViewSql(const IRdbViewInfo &info) const
{
    return "DROP VIEW IF EXISTS " + quoteName(info.m_entityName);
}

QString IRdbDialectWare::countSql(const IRdbEntityInfo &info) const
{
    return "SELECT count(1) FROM " + quoteName(info.m_entityName);
}

QString IRdbDialectWare::countSql(const IRdbEntityInfo &info, const IRdbCondition &condition) const
{
    return "SELECT count(1) FROM " + quoteName(info.m_entityName) + " " + conditionToSql(condition);
}

void IRdbDialectWare::insert(ISqlQuery &query, const IRdbTableInfo &info, void *ptr) const
{
    QStringList names, values;
    for(int index=0; index<info.m_fields.length(); index++){
        if(info.m_autoIncrement == index){
            continue;
        }

        const auto& field = info.m_fields[index];
        const auto& maker = info.m_valueMakers[index];
        names.append(field.m_name);
        if(maker.type == IRdbTableInfo::ValueMakerType::InsertValue){
            values.append(maker.insertValue);
        }else if(maker.type == IRdbTableInfo::ValueMakerType::GenerateValue){
            auto valueName = ":" + field.m_name;
            values.append(valueName);
            auto value = maker.generator();
            IMetaUtil::writeProperty(field.m_property, ptr, value);
            query.bindParameter(valueName, value);
        }else{
            auto valueName = ":" + field.m_name;
            values.append(valueName);
            query.bindParameter(valueName, IMetaUtil::readProperty(field.m_property, ptr));
        }
    }

    auto sql = QString("INSERT INTO ")
            .append(quoteName(info.m_entityName)) .append(" (")
            .append(names.join(", ")).append( ") VALUES (").append(values.join(", ")).append(")");
    query.prepare(sql);
}

void IRdbDialectWare::insert(ISqlQuery& query, const IRdbTableInfo &info, const void * ptr) const
{
    QStringList names, values;
    for(int index=0; index<info.m_fields.length(); index++){
        if(info.m_autoIncrement == index){
            continue;
        }

        const auto& field = info.m_fields[index];
        const auto& maker = info.m_valueMakers[index];
        names.append(field.m_name);
        if(maker.type == IRdbTableInfo::ValueMakerType::InsertValue){
            values.append(maker.insertValue);
        }else if(maker.type == IRdbTableInfo::ValueMakerType::GenerateValue){
            auto valueName = ":" + field.m_name;
            values.append(valueName);
            query.bindParameter(valueName, maker.generator());
        }else{
            auto valueName = ":" + field.m_name;
            values.append(valueName);
            query.bindParameter(valueName, IMetaUtil::readProperty(field.m_property, ptr));
        }
    }

    auto sql = QString("INSERT INTO ")
            .append(quoteName(info.m_entityName)) .append(" (")
            .append(names.join(", ")).append( ") VALUES (").append(values.join(", ")).append(")");
    query.prepare(sql);
}

void IRdbDialectWare::insertAll(ISqlQuery &query, const IRdbTableInfo &info, QVector<const void *>ptrs) const
{
    QStringList names;
    QVector<QStringList> values;
    int count = ptrs.length();
    for(int i=0; i<count; i++){
        values.append(QStringList{});
    }

    for(int index=0; index<info.m_fields.length(); index++){
        if(info.m_autoIncrement == index){
            continue;
        }

        const auto& field = info.m_fields[index];
        const auto& maker = info.m_valueMakers[index];
        names.append(field.m_name);
        if(maker.type == IRdbTableInfo::ValueMakerType::InsertValue){
            for(int i=0; i<=count; i++){
                values[i].append(maker.insertValue);
            }
        }else if(maker.type == IRdbTableInfo::ValueMakerType::GenerateValue){
            for(int i=0; i<count; i++){
                auto valueName = ":" + field.m_name + "_" + QString::number(i);
                values[i].append(valueName);
                query.bindParameter(valueName, maker.generator());
            }
        }else {
            for(int i=0; i<count; i++){
                auto valueName = ":" + field.m_name + "_" + QString::number(i);
                values[i].append(valueName);
                query.bindParameter(valueName, IMetaUtil::readProperty(field.m_property, ptrs[i]));
            }
        }
    }

    QStringList args;
    args.reserve(values.length());
    for(const QStringList& list : values){
        args.append(list.join(", "));
    }
    auto sql = QString("INSERT INTO ")
            .append(quoteName(info.m_entityName)) .append(" (")
            .append(names.join(", ")).append( ") VALUES (").append(args.join("), (")).append(")");
    query.prepare(sql);
}

QString IRdbDialectWare::findOneSql(const IRdbEntityInfo &info, const IRdbCondition &condition) const
{
    return "SELECT * FROM " + quoteName(info.m_entityName) + " " + conditionToSql(condition);
}

QString IRdbDialectWare::findAllSql(const IRdbEntityInfo &info) const
{
    return "SELECT * FROM " + quoteName(info.m_entityName);
}

QString IRdbDialectWare::findAllSql(const IRdbEntityInfo &info, const IRdbCondition &condition) const
{
    return "SELECT * FROM " + quoteName(info.m_entityName) + " " + conditionToSql(condition);
}

QString IRdbDialectWare::findColumnSql(const IRdbEntityInfo &info, const QStringList &columns) const
{
    QString sql = "SELECT ";
    sql.append(columns.join(", ")).append(" FROM ").append(quoteName(info.m_entityName));
    return sql;
}

QString IRdbDialectWare::findColumnSql(const IRdbEntityInfo &info, const QStringList &columns, const IRdbCondition &condition) const
{
    QString sql = "SELECT ";
    sql.append(columns.join(", ")).append(" FROM ").append(quoteName(info.m_entityName)).append(conditionToSql(condition));
    return sql;
}

QString IRdbDialectWare::existSql(const IRdbEntityInfo &info, const IRdbCondition &condition) const
{
    return "SELECT EXISTS ( SELECT 1 FROM " + quoteName(info.m_entityName) + conditionToSql(condition) + ")";
}

QString IRdbDialectWare::updateOne(const IRdbTableInfo &info, const QStringList &columns) const
{
    QStringList args;
    QString id = info.m_fields[info.m_primaryKey].m_name;
    for(const QString& col : columns){
        if(col != id){
            args.append(col + "= :" + col);
        }
    }

    return QString("UPDATE ").append(quoteName(info.m_entityName))
            .append(" SET ").append(args.join(", "))
            .append(" WHERE " ).append(id).append(" = :").append(id);
}

QString IRdbDialectWare::updateWhere(const IRdbTableInfo& info, const QVariantMap &map, const IRdbCondition &condition) const
{
    QStringList args;
    const auto& keys = map.keys();
    for(const QString& col : keys){
        args.append(col + "= :" + col);
    }

    return QString("UPDATE ").append(quoteName(info.m_entityName))
            .append(" SET ").append(args.join(", "))
            .append(conditionToSql(condition));
}

QString IRdbDialectWare::deleteTableSql(const IRdbEntityInfo &info) const
{
    return "DELETE FROM " + quoteName(info.m_entityName);
}

QString IRdbDialectWare::deleteTableSql(const IRdbEntityInfo &info, const IRdbCondition &condition) const
{
    return "DELETE FROM " + quoteName(info.m_entityName) + conditionToSql(condition);
}

QString IRdbDialectWare::truncateTableSql(const IRdbEntityInfo &info) const
{
    return "TRUNCATE TABLE " + quoteName(info.m_entityName);
}

QString IRdbDialectWare::conditionToSql(const IRdbCondition & condition) const
{
    auto sql = toWhereSql(condition);
    sql += toGroupBySql(condition);
    sql += toOrderBySql(condition);
    sql += toLimitSql(condition);
    sql += toHavingSql(condition);
    return sql;
}

QString IRdbDialectWare::toWhereSql(const IRdbCondition &condition) const
{
    QString sql;
    int count = static_cast<int>(condition.m_impl->m_wheres.size() + condition.m_impl->m_conditions.size());
    if(count == 0){
        return {};
    }
    bool isAnd = true;
    for(int i=0; i<count; i++){
        QString where;
        if(condition.m_impl->m_wheres.count(i)){
            const auto& arg = condition.m_impl->m_wheres[i];
            where = fromWhereClause(arg);
            isAnd = arg.m_isAnd;
        }else{
            const auto& arg = condition.m_impl->m_conditions[i];
            where = " (" + toWhereSql(arg).trimmed() + ")";
            if(arg.m_impl->m_isNot){
                where = " NOT" + where;
            }
            isAnd = arg.m_impl->m_isAnd;
        }

        if(i == 0){
            sql = where;
        }else{
            sql += (isAnd ? " AND" : " OR") + where;
        }
    }
    return condition.m_impl->m_isChild ? sql : (" WHERE" + sql);
}

QString IRdbDialectWare::toOrderBySql(const IRdbCondition &condition) const
{
    if(condition.m_impl->m_orderBys.empty()){
        return {};
    }

    QStringList orders;
    for(const auto& order : condition.m_impl->m_orderBys){
        orders.append(fromOrderByClause(order));
    }
    return " ORDER BY" + orders.join(",");
}

QString IRdbDialectWare::toGroupBySql(const IRdbCondition &condition) const
{
    if(condition.m_impl->m_groupBys.empty()){
        return {};
    }

    QString sql = " GROUP BY";
    QStringList groups;
    for(const auto& groupBy : condition.m_impl->m_groupBys){
        groups.append(fromGroupByClause(groupBy));
    }
    return " GROUP BY" + groups.join(",");
}

QString IRdbDialectWare::toHavingSql(const IRdbCondition &condition) const
{
    if(condition.m_impl->m_havings.empty()){
        return {};
    }

    QString sql;
    QStringList havings;
    if(condition.m_impl->m_havings.size() >= 1){
        auto first = condition.m_impl->m_havings.front();
        condition.m_impl->m_havings.pop_front();
        havings.append(fromHavingClause(first));
    }

    for(const auto& having : condition.m_impl->m_havings){
        auto clause = fromHavingClause(having);
        if(sql.isEmpty()){
            bool isAnd = ((having.m_relation == IRdb::Relation::And) ||(having.m_relation == IRdb::Relation::AndNot));
            clause = (isAnd ? " AND" : " OR") + clause;
        }
        havings.append(clause);
    }
    return " HAVING" + havings.join("");
}

QString IRdbDialectWare::toLimitSql(const IRdbCondition &condition) const
{
    return fromLimitClause(condition.m_impl->m_limit);
}

QString IRdbDialectWare::fromWhereClause(const IRdbWhereClause &where) const
{
    if(where.m_isNot){
        return " NOT (" + fromWhereClauseImpl(where) + ")";
    }
    return " " + fromWhereClauseImpl(where);
}

QString IRdbDialectWare::fromWhereClauseImpl(const IRdbWhereClause & where) const
{
    switch (where.m_type)
    {
    case IRdbWhereClause::Type::Where: {
        return where.m_arguments.first();
    }
    case IRdbWhereClause::Type::WhereLike: {
        auto name = getVividName(where.m_field);
        where.m_boundValue[name] = "%" + where.m_arguments.first() + "%";
        return where.m_field + " LIKE " + name;
    }
    case IRdbWhereClause::Type::whereNotLike: {
        auto name = getVividName(where.m_field);
        where.m_boundValue[name] = "%" + where.m_arguments.first() + "%";
        return where.m_field + " NOT LIKE " + name;
    }
    case IRdbWhereClause::Type::WhereEndWith: {
        auto name = getVividName(where.m_field);
        where.m_boundValue[name] = where.m_arguments.first() + "%";
        return where.m_field + " LIKE " + name;
    }
    case IRdbWhereClause::Type::WhereStartWith: {
        auto name = getVividName(where.m_field);
        where.m_boundValue[name] = "%" + where.m_arguments.first();
        return where.m_field + " LIKE " + name;
    }
    case IRdbWhereClause::Type::WhereBetween: {
        auto name1 = getVividName(where.m_field);
        auto name2 = getVividName(where.m_field);
        where.m_boundValue[name1] = where.m_variants.first();
        where.m_boundValue[name2] = where.m_variants.last();
        return where.m_field + " BETWEEN " + name1 + " AND " + name2;
    }
    case IRdbWhereClause::Type::WhereIn:{
        QStringList names;
        for(const auto& var : where.m_variants){
            auto name = getVividName(where.m_field);
            where.m_boundValue[name] = var;
            names << name;
        }
        return where.m_field + " IN (" + names.join(", ") + ")";
    }
    case IRdbWhereClause::Type::WhereEqual: {
        auto name = getVividName(where.m_field);
        where.m_boundValue[name] = where.m_variants.first();
        return where.m_field + " = " + name;
    }
    case IRdbWhereClause::Type::WhereNotEqual: {
        auto name = getVividName(where.m_field);
        where.m_boundValue[name] = where.m_variants.first();
        return where.m_field + " <> " + name;
    }
    case IRdbWhereClause::Type::WhereGreaterThan: {
        auto name = getVividName(where.m_field);
        where.m_boundValue[name] = where.m_variants.first();
        return where.m_field + " > " + name;
    }
    case IRdbWhereClause::Type::WhereGreaterEqual: {
        auto name = getVividName(where.m_field);
        where.m_boundValue[name] = where.m_variants.first();
        return where.m_field + " >= " + name;
    }
    case IRdbWhereClause::Type::WhereLessThan: {
        auto name = getVividName(where.m_field);
        where.m_boundValue[name] = where.m_variants.first();
        return where.m_field + " < " + name;
    }
    case IRdbWhereClause::Type::WhereLessEqual: {
        auto name = getVividName(where.m_field);
        where.m_boundValue[name] = where.m_variants.first();
        return where.m_field + " <= " + name;
    }
    case IRdbWhereClause::Type::WhereIsNull: {
        return where.m_field + " IS NULL";
    }
    case IRdbWhereClause::Type::WhereIsNotNull:{
        return where.m_field + " IS NOT NULL";
    }
    case IRdbWhereClause::Type::WhereTrue: {
        return "1 = 1";
    }
    case IRdbWhereClause::Type::WhereFalse: {
        return "1 <> 1";
    }
    }
    QString tip = "where clause type does not match anything, please check";
    IRdbAbort::abortDialectError(tip, $ISourceLocation);
    return "";
}

QString IRdbDialectWare::fromOrderByClause(const IRdbOrderByClause & order) const
{
    return " " + order.m_field + (order.m_isAscending ? " ASC" : " DESC");
}

QString IRdbDialectWare::fromLimitClause(const IRdbLimitClause &limit) const
{
    if(limit.m_limit < 0){
        return {};
    }
    QString sql = " LIMIT " + QString::number(limit.m_limit);
    if(limit.m_offset >0){
        sql += " OFFSET " + QString::number(limit.m_offset);
    }
    return sql;
}

QString IRdbDialectWare::fromGroupByClause(const IRdbGroupByClause &group) const
{
    return " " + group.m_field;
}

QString IRdbDialectWare::fromHavingClause(const IRdbHavingClause &having) const
{
    bool isNot = (having.m_relation == IRdb::Relation::AndNot) || (having.m_relation == IRdb::Relation::OrNot);
    if(isNot){
        return " NOT (" + having.m_havingSql + ")";
    }
    return " " + having.m_havingSql;
}

QString IRdbDialectWare::createSqlCommonKeyClause(const IRdbTableInfo &info, int index) const
{
    const auto& name = quoteName(info.m_fieldNames[index]);
    auto sqlType = getSqlType(info, index);

    QString piece = name + " " + sqlType;
    if(info.m_notNullKeys.contains(index)){
        piece.append(" NOT NULL");
    }
    if(info.m_uniqueKeys.contains(index)){
        piece.append(" UNIQUE");
    }
    if(info.m_primaryKey == index){
        piece.append(" PRIMARY KEY");
    }
    if(info.m_autoIncrement == index){
        piece.append(" AUTOINCREMENT");
    }
    if(info.m_constraints.contains(index)){
        piece.append(" ").append(info.m_constraints[index]);
    }
    return piece;
}

void IRdbDialectWare::bindParameter(QSqlQuery &query, const QString &field, const QVariant &value) const
{
    if((static_cast<QMetaType::Type>(IMetaUtil::typeId(value)) >= QMetaType::User)
            && ((value.typeName() == std::string("std::string"))
                || (value.typeName() == std::string("IString")))){
        return query.bindValue(field, value.value<QString>());
    }
    query.bindValue(field, value);
}

QString IRdbDialectWare::quoteName(const QString &name) const
{
    return "\"" + name + "\"";
}

QString IRdbDialectWare::getVividName(const QString &name)
{
    static std::atomic_uint64_t value {};
    return ":" + name + "_" + QString::number(value++);
}

$PackageWebCoreEnd
