#pragma once

#include "core/util/IHeaderUtil.h"
#include "core/base/IResult.h"
#include "rdb/ISqlQuery.h"
#include "rdb/IRdbUtil.h"
#include "rdb/dialect/IRdbDialectWare.h"
#include "rdb/clause/IRdbCondition.h"
#include "rdb/database/IRdbDatabaseWare.h"
#include "rdb/exception/IRdbException.h"
#include "rdb/entity/IRdbEntityInfo.h"

$PackageWebCoreBegin

template<typename Entity, typename Db>
class IRdbEntityModelWare
{
public:
    using DbType = Db;

public:
    IRdbEntityModelWare();

public:
    std::size_t count();
    std::size_t count(const IRdbCondition&);

public:
    IResult<Entity> findOne(const IRdbCondition&);
    Entity findOneRaw(const IRdbCondition&);
    QList<Entity> findAll();
    QList<Entity> findAll(const IRdbCondition&);
    QVariantList findColumn(const QString& column);
    QVariantList findColumn(const QString& column, const IRdbCondition& condition);
    QList<QVariantMap> findColumns(const QStringList& columns);
    QList<QVariantMap> findColumns(const QStringList& columns, const IRdbCondition& condition);

public:
    bool exist(const IRdbCondition& condition);

public:
    ISqlQuery createQuery();
    ISqlQuery createQuery(const QString& sql);
    ISqlQuery createQuery(const QString& sql, const QVariantMap& values);

protected:
    const IRdbEntityInfo& entityInfo() const;

protected:
    IRdbDatabaseWare& m_database;
    const IRdbDialectWare& m_dialect;
};

template<typename Entity, typename Db>
IRdbEntityModelWare<Entity, Db>::IRdbEntityModelWare()
    : m_database(Db::instance()), m_dialect(Db::DialectType::instance())
{
}

template<typename Entity, typename Db>
std::size_t IRdbEntityModelWare<Entity, Db>::count()
{
    auto query = createQuery(m_dialect.countSql(entityInfo()));
    query.exec();
    bool ok = true;
    auto value = IRdbUtil::getLongLong(query, ok);
    return ok ? value : 0;
}

template<typename Entity, typename Db>
std::size_t IRdbEntityModelWare<Entity, Db>::count(const IRdbCondition & condition)
{
    auto query = createQuery(m_dialect.countSql(entityInfo(), condition));
    condition.bindParameters(query);
    query.exec();
    bool ok = true;
    auto value = IRdbUtil::getLongLong(query, ok);
    return ok ? value : 0;
}

template<typename Entity, typename Db>
IResult<Entity> IRdbEntityModelWare<Entity, Db>::findOne(const IRdbCondition& condition)
{
    auto sql =m_dialect.findOneSql(entityInfo(), condition);
    auto query = createQuery(sql);
    condition.bindParameters(query);
    if(!query.exec()){
        if(query.lastError().type() != QSqlError::NoError){
            throw IRdbException(query.lastError());
        }
        return std::nullopt;
    }
    return IRdbUtil::getEntity<Entity>(query);
}

template<typename Entity, typename Db>
Entity IRdbEntityModelWare<Entity, Db>::findOneRaw(const IRdbCondition & condition)
{
    auto val = findOne(condition);
    if(val){
        return *val;
    }
    return {};
}

template<typename Entity, typename Db>
QList<Entity> IRdbEntityModelWare<Entity, Db>::findAll()
{
    auto query = createQuery(m_dialect.findAllSql(entityInfo()));
    query.exec();
    return IRdbUtil::getEntities<Entity>(query);
}

template<typename Entity, typename Db>
QList<Entity> IRdbEntityModelWare<Entity, Db>::findAll(const IRdbCondition& condition)
{
    auto query = createQuery(m_dialect.findAllSql(entityInfo(), condition));
    condition.bindParameters(query);
    query.exec();
    return IRdbUtil::getEntities<Entity>(query);
}

template<typename Entity, typename Db>
QVariantList IRdbEntityModelWare<Entity, Db>::findColumn(const QString& column)
{
    auto query = createQuery(m_dialect.findColumnSql(entityInfo(), {column}));
    if(!query.exec()){
        return {};
    }
    return IRdbUtil::getVariantList(query);
}

template<typename Entity, typename Db>
QVariantList IRdbEntityModelWare<Entity, Db>::findColumn(const QString &column, const IRdbCondition &condition)
{
    auto query = createQuery(m_dialect.findColumnSql(entityInfo(), {column}, condition));
    condition.bindParameters(query);
    if(!query.exec()){
        return {};
    }
    return IRdbUtil::getVariantList(query);
}

template<typename Entity, typename Db>
QList<QVariantMap> IRdbEntityModelWare<Entity, Db>::findColumns(const QStringList& columns)
{
    auto query = createQuery(m_dialect.findColumnSql(entityInfo(), columns));
    if(!query.exec()){
        return {};
    }
    return IRdbUtil::getVariantMapList(query);
}

template<typename Entity, typename Db>
QList<QVariantMap> IRdbEntityModelWare<Entity, Db>::findColumns(const QStringList& columns, const IRdbCondition& condition)
{
    auto query = createQuery(m_dialect.findColumnSql(entityInfo(), columns, condition));
    condition.bindParameters(query);
    if(!query.exec()){
        return {};
    }
    return IRdbUtil::getVariantMapList(query);
}

template<typename Entity, typename Db>
bool IRdbEntityModelWare<Entity, Db>::exist(const IRdbCondition &condition)
{
    auto query = createQuery(m_dialect.existSql(entityInfo(), condition));
    condition.bindParameters(query);
    if(!query.exec()){
        return false;
    }
    auto value = IRdbUtil::getBool(query);
    if(value){
        return *value;
    }
    return false;
}

template<typename Entity, typename Db>
ISqlQuery IRdbEntityModelWare<Entity, Db>::createQuery()
{
    return m_database.createQuery();
}

template<typename Entity, typename Db>
ISqlQuery IRdbEntityModelWare<Entity, Db>::createQuery(const QString &sql)
{
    auto query = m_database.createQuery();
    query.prepare(sql);
    return query;
}

template<typename Entity, typename Db>
ISqlQuery IRdbEntityModelWare<Entity, Db>::createQuery(const QString& sql, const QVariantMap& values)
{
    auto query = m_database.createQuery();
    query.prepare(sql);
    query.bindParameters(values);
    return query;
}

template<typename Entity, typename Db>
const IRdbEntityInfo &IRdbEntityModelWare<Entity, Db>::entityInfo() const
{
    return Entity::staticEntityInfo();
}

$PackageWebCoreEnd
