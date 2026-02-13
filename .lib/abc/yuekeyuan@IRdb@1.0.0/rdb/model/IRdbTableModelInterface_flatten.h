#pragma once

#ifdef IWEBCORE_FLATTEN_CRTP

#include "core/util/IHeaderUtil.h"
#include "core/task/unit/ITaskWareUnit.h"
#include "core/base/IResult.h"
#include "rdb/IRdbAbort.h"
#include "rdb/IRdbUtil.h"
#include "rdb/IRdbCatagory.h"
#include "rdb/ISqlQuery.h"
#include "rdb/clause/IRdbCondition.h"
#include "rdb/entity/IRdbTableInfo.h"
#include "rdb/model/IRdbEntityModelWare.h"

$PackageWebCoreBegin

template<typename T, typename Table, typename Db, bool enabled = true>
class IRdbTableModelInterface : public ITaskWare
{
    $AsTaskUnit(IRdbTableModelInterface)
    Q_DISABLE_COPY_MOVE(IRdbTableModelInterface)
public:
    IRdbTableModelInterface();

// taskware
protected:
    virtual const std::string& $name() const final;
    virtual const std::string& $catagory() const final;

// Entity model ware
public:
    std::size_t count();
    std::size_t count(const IRdbCondition&);

public:
    IResult<Table> findOne(const IRdbCondition&);
    Table findOneRaw(const IRdbCondition&);
    QList<Table> findAll();
    QList<Table> findAll(const IRdbCondition&);
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

// table model interface
public:
    int insert(const QString& sql, const QVariantMap& values);
    int insertOneRef(Table& table);
    int insertOne(const Table& table);
    int insertAll(const QList<Table>& tables);

public:
    bool existById(const QVariant& id);

public:
    IResult<Table> findById(const QVariant& id);
    Table findByIdRaw(const QVariant& id);
    QList<Table> findAllByIds(const QVariantList& list);

public:
    int update(const QString& sql, const QVariantMap& values);
    int updateOne(const Table& table);
    int updateOne(const Table& table, const QStringList& columns);
    int updateAll(const QList<Table>& tables);
    int updateAll(const QList<Table>& tables, const QStringList& columns);
    int updateWhere(const QVariantMap& map, const IRdbCondition& condition);
    int updateById(const QVariant& id, const QVariantMap& map);

public:
    int deleted(const QString& sql, const QVariantMap& values);
    int deleteOne(const Table&);
    int deleteAll();
    int deleteAll(const QList<Table>& tables);
    int deleteAll(const IRdbCondition& condition);
    int deleteById(const QVariant& id);
    int deleteAllByIds(const QVariantList& ids);

public:
    virtual QString createTableSql() const;

public:
    void createTable();
    void clearTable();
    void truncateTable();

private:
    bool containsTable(const QString& tableName);

protected: // only self use and son use
    const IRdbTableInfo& tableInfo() const;

protected:
    virtual double $order() const override;
    virtual void $task() final;
};

template<typename T, typename Table, typename Db, bool enabled>
const std::string& IRdbTableModelInterface<T, Table, Db, enabled>::$name() const
{
    static const std::string name = IMetaUtil::getBareTypeName<T>();
    return name;
}

template<typename T, typename Table, typename Db, bool enabled>
const std::string& IRdbTableModelInterface<T, Table, Db, enabled>::$catagory() const
{
    static const std::string name = IMetaUtil::getBareTypeName<IRdbCatagory>();
    return name;
}

template<typename T, typename Table, typename Db, bool enabled>
std::size_t IRdbTableModelInterface<T, Table, Db, enabled>::count()
{
    auto query = createQuery(m_dialect.countSql(entityInfo()));
    query.exec();
    bool ok = true;
    auto value = IRdbUtil::getLongLong(query, ok);
    return ok ? value : 0;
}

template<typename T, typename Table, typename Db, bool enabled>
std::size_t IRdbTableModelInterface<T, Table, Db, enabled>::count(const IRdbCondition & condition)
{
    auto query = createQuery(m_dialect.countSql(entityInfo(), condition));
    condition.bindParameters(query);
    query.exec();
    bool ok = true;
    auto value = IRdbUtil::getLongLong(query, ok);
    return ok ? value : 0;
}

template<typename T, typename Table, typename Db, bool enabled>
IResult<Table> IRdbTableModelInterface<T, Table, Db, enabled>::findOne(const IRdbCondition& condition)
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
    return IRdbUtil::getEntity<Table>(query);
}

template<typename T, typename Table, typename Db, bool enabled>
Table IRdbTableModelInterface<T, Table, Db, enabled>::findOneRaw(const IRdbCondition & condition)
{
    auto val = findOne(condition);
    if(val){
        return *val;
    }
    return {};
}

template<typename T, typename Table, typename Db, bool enabled>
QList<Table> IRdbTableModelInterface<T, Table, Db, enabled>::findAll()
{
    auto query = createQuery(m_dialect.findAllSql(entityInfo()));
    query.exec();
    return IRdbUtil::getEntities<Table>(query);
}

template<typename T, typename Table, typename Db, bool enabled>
QList<Table> IRdbTableModelInterface<T, Table, Db, enabled>::findAll(const IRdbCondition& condition)
{
    auto query = createQuery(m_dialect.findAllSql(entityInfo(), condition));
    condition.bindParameters(query);
    query.exec();
    return IRdbUtil::getEntities<Table>(query);
}

template<typename T, typename Table, typename Db, bool enabled>
QVariantList IRdbTableModelInterface<T, Table, Db, enabled>::findColumn(const QString& column)
{
    auto query = createQuery(m_dialect.findColumnSql(entityInfo(), {column}));
    if(!query.exec()){
        return {};
    }
    return IRdbUtil::getVariantList(query);
}

template<typename T, typename Table, typename Db, bool enabled>
QVariantList IRdbTableModelInterface<T, Table, Db, enabled>::findColumn(const QString &column, const IRdbCondition &condition)
{
    auto query = createQuery(m_dialect.findColumnSql(entityInfo(), {column}, condition));
    condition.bindParameters(query);
    if(!query.exec()){
        return {};
    }
    return IRdbUtil::getVariantList(query);
}

template<typename T, typename Table, typename Db, bool enabled>
QList<QVariantMap> IRdbTableModelInterface<T, Table, Db, enabled>::findColumns(const QStringList& columns)
{
    auto query = createQuery(m_dialect.findColumnSql(entityInfo(), columns));
    if(!query.exec()){
        return {};
    }
    return IRdbUtil::getVariantMapList(query);
}

template<typename T, typename Table, typename Db, bool enabled>
QList<QVariantMap> IRdbTableModelInterface<T, Table, Db, enabled>::findColumns(const QStringList& columns, const IRdbCondition& condition)
{
    auto query = createQuery(m_dialect.findColumnSql(entityInfo(), columns, condition));
    condition.bindParameters(query);
    if(!query.exec()){
        return {};
    }
    return IRdbUtil::getVariantMapList(query);
}

template<typename T, typename Table, typename Db, bool enabled>
bool IRdbTableModelInterface<T, Table, Db, enabled>::exist(const IRdbCondition &condition)
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

template<typename T, typename Table, typename Db, bool enabled>
ISqlQuery IRdbTableModelInterface<T, Table, Db, enabled>::createQuery()
{
    return m_database.createQuery();
}

template<typename T, typename Table, typename Db, bool enabled>
ISqlQuery IRdbTableModelInterface<T, Table, Db, enabled>::createQuery(const QString &sql)
{
    auto query = m_database.createQuery();
    query.prepare(sql);
    return query;
}

template<typename T, typename Table, typename Db, bool enabled>
ISqlQuery IRdbTableModelInterface<T, Table, Db, enabled>::createQuery(const QString& sql, const QVariantMap& values)
{
    auto query = m_database.createQuery();
    query.prepare(sql);
    query.bindParameters(values);
    return query;
}

template<typename T, typename Table, typename Db, bool enabled>
const IRdbEntityInfo &IRdbTableModelInterface<T, Table, Db, enabled>::entityInfo() const
{
    return Table::staticEntityInfo();
}

template<typename T, typename Table, typename Db, bool enabled>
IRdbTableModelInterface<T, Table, Db, enabled>::IRdbTableModelInterface()
    : m_database(Db::instance()), m_dialect(Db::DialectType::instance())
{
}

template<typename T, typename Table, typename Db, bool enabled>
int IRdbTableModelInterface<T, Table, Db, enabled>::insert(const QString &sql, const QVariantMap &values)
{
    ISqlQuery query = this->createQuery(sql, values);
    query.exec();
    return query.numRowsAffected();
}

template<typename T, typename Table, typename Db, bool enabled>
int IRdbTableModelInterface<T, Table, Db, enabled>::insertOneRef(Table &table)
{
    ISqlQuery query = this->createQuery();
    this->m_dialect.insert(query, tableInfo(), &table);
    query.exec();

    const auto& maker = tableInfo().m_valueMakers[tableInfo().m_primaryKey];
    if(maker.type == IRdbTableInfo::ValueMakerType::InsertValue){   // TODO: 这个有点意思
        IMetaUtil::writeProperty(tableInfo().m_fields[tableInfo().m_primaryKey].m_property, &table, query.lastInsertId());
    }else if(maker.type == IRdbTableInfo::ValueMakerType::ReadValue){
        IMetaUtil::writeProperty(tableInfo().m_fields[tableInfo().m_primaryKey].m_property, &table, query.lastInsertId());
    }
    return query.numRowsAffected();
}

template<typename T, typename Table, typename Db, bool enabled>
int IRdbTableModelInterface<T, Table, Db, enabled>::insertOne(const Table& table)
{
    ISqlQuery query = this->createQuery();
    this->m_dialect.insert(query, tableInfo(), &table);
    query.exec();
    return query.numRowsAffected();
}

template<typename T, typename Table, typename Db, bool enabled>
int IRdbTableModelInterface<T, Table, Db, enabled>::insertAll(const QList<Table> &tables)
{
    QVector<const void*> ptrs;
    for(const auto& table : tables){
        ptrs.append(&table);
    }

    ISqlQuery query = this->createQuery();
    this->m_dialect.insertAll(query, tableInfo(), ptrs);
    query.exec();
    return query.numRowsAffected();
}

template<typename T, typename Table, typename Db, bool enabled>
bool IRdbTableModelInterface<T, Table, Db, enabled>::existById(const QVariant &id)
{
    auto name = tableInfo().m_fields[tableInfo().m_primaryKey].m_name;
    return this->exist(IRdb::whereEqual(name, id));
}

template<typename T, typename Table, typename Db, bool enabled>
IResult<Table> IRdbTableModelInterface<T, Table, Db, enabled>::findById(const QVariant& id)
{
    auto name = tableInfo().m_fields[tableInfo().m_primaryKey].m_name;
    return this->findOne(IRdb::whereEqual(name, id));
}

template<typename T, typename Table, typename Db, bool enabled>
Table IRdbTableModelInterface<T, Table, Db, enabled>::findByIdRaw(const QVariant &id)
{
    auto val = findById(id);
    if(val){
        return *val;
    }
    return {};
}

template<typename T, typename Table, typename Db, bool enabled>
QList<Table> IRdbTableModelInterface<T, Table, Db, enabled>::findAllByIds(const QVariantList& list)
{
    auto name = tableInfo().m_fields[tableInfo().m_primaryKey].m_name;
    return this->findAll(IRdb::whereIn(name, list));
}

template<typename T, typename Table, typename Db, bool enabled>
int IRdbTableModelInterface<T, Table, Db, enabled>::update(const QString& sql, const QVariantMap& values)
{
    auto query = this->createQuery(sql, values);
    query.exec();
    return query.numRowsAffected();
}

template<typename T, typename Table, typename Db, bool enabled>
int IRdbTableModelInterface<T, Table, Db, enabled>::updateOne(const Table& table)
{
    return updateOne(table, tableInfo().m_fieldNames);
}

template<typename T, typename Table, typename Db, bool enabled>
int IRdbTableModelInterface<T, Table, Db, enabled>::updateOne(const Table &table, const QStringList &columns)
{
    auto query = this->createQuery(this->m_dialect.updateOne(tableInfo(), columns));
    for(const auto& field : tableInfo().m_fields){
        query.bindParameter(":" + field.m_name, IMetaUtil::readProperty(field.m_property, &table));
    }
    query.exec();
    return query.numRowsAffected();
}

template<typename T, typename Table, typename Db, bool enabled>
int IRdbTableModelInterface<T, Table, Db, enabled>::updateAll(const QList<Table> &tables)
{
    int numberOfRows {};
    for(const auto& table : tables){
        numberOfRows += updateOne(table);
    }
    return numberOfRows;
}

template<typename T, typename Table, typename Db, bool enabled>
int IRdbTableModelInterface<T, Table, Db, enabled>::updateAll(const QList<Table> &tables, const QStringList& columns)
{
    int numberOfRows {};
    for(const auto& table : tables){
        numberOfRows += updateOne(table, columns);
    }
    return numberOfRows;
}

template<typename T, typename Table, typename Db, bool enabled>
int IRdbTableModelInterface<T, Table, Db, enabled>::updateWhere(const QVariantMap &map, const IRdbCondition &condition)
{
    auto query = this->createQuery(this->m_dialect.updateWhere(tableInfo(), map, condition));
    condition.bindParameters(query);
    QStringList keys = map.keys();
    for(const auto& key : keys){
        query.bindParameter(":" + key, map[key]);
    }
    query.exec();
    return query.numRowsAffected();
}

template<typename T, typename Table, typename Db, bool enabled>
int IRdbTableModelInterface<T, Table, Db, enabled>::updateById(const QVariant &id, const QVariantMap &map)
{
    IRdbCondition condition = IRdb::whereEqual(tableInfo().m_fields[tableInfo().m_primaryKey].m_name, id);
    return updateWhere(map, condition);
}

template<typename T, typename Table, typename Db, bool enabled>
int IRdbTableModelInterface<T, Table, Db, enabled>::deleted(const QString& sql, const QVariantMap& values)
{
    auto query = this->createQuery(sql, values);
    return query.numRowsAffected();
}

template<typename T, typename Table, typename Db, bool enabled>
int IRdbTableModelInterface<T, Table, Db, enabled>::deleteOne(const Table& table)
{
    const auto& field = tableInfo().m_fields[tableInfo().m_primaryKey];
    auto value = IMetaUtil::readProperty(field.m_property, &table);
    return deleteById(value);
}

template<typename T, typename Table, typename Db, bool enabled>
int IRdbTableModelInterface<T, Table, Db, enabled>::deleteAll()
{
    auto query = this->createQuery(this->m_dialect.deleteTableSql(tableInfo()));
    query.exec();
    return query.numRowsAffected();
}

template<typename T, typename Table, typename Db, bool enabled>
int IRdbTableModelInterface<T, Table, Db, enabled>::deleteAll(const QList<Table>& tables)
{
    QVariantList list;
    const QMetaProperty& property = tableInfo().m_fields[tableInfo().m_primaryKey].m_property;
    for(const auto& table : tables){
        list.append(IMetaUtil::readProperty(property, &table));
    }

    return deleteAllByIds(list);
}

template<typename T, typename Table, typename Db, bool enabled>
int IRdbTableModelInterface<T, Table, Db, enabled>::deleteAll(const IRdbCondition& condition)
{
    auto query = this->createQuery(this->m_dialect.deleteTableSql(tableInfo(), condition));
    condition.bindParameters(query);
    query.exec();
    return query.numRowsAffected();
}

template<typename T, typename Table, typename Db, bool enabled>
int IRdbTableModelInterface<T, Table, Db, enabled>::deleteById(const QVariant& id)
{
    auto name = tableInfo().m_fields[tableInfo().m_primaryKey].m_name;
    return deleteAll(IRdb::whereEqual(name, id));
}

template<typename T, typename Table, typename Db, bool enabled>
int IRdbTableModelInterface<T, Table, Db, enabled>::deleteAllByIds(const QVariantList& ids)
{
    auto name = tableInfo().m_fields[tableInfo().m_primaryKey].m_name;
    return deleteAll(IRdb::whereIn(name, ids));
}

template<typename T, typename Table, typename Db, bool enabled>
QString IRdbTableModelInterface<T, Table, Db, enabled>::createTableSql() const
{
    return {};
}

template<typename T, typename Table, typename Db, bool enabled>
void IRdbTableModelInterface<T, Table, Db, enabled>::createTable()
{
    auto sql = createTableSql();
    if(sql.isEmpty()){
        sql = this->m_dialect.createTableSql(tableInfo());
    }
    if(sql.isEmpty()){
        IRdbAbort::abortEntityCannotBeCreated("no create table sql clause exist, please add createTableSql", $ISourceLocation);
    }

    qDebug() << "table created" << typeid(Table).name();

    this->createQuery().exec(sql);
}

template<typename T, typename Table, typename Db, bool enabled>
void IRdbTableModelInterface<T, Table, Db, enabled>::clearTable()
{
    deleteAll();
}

template<typename T, typename Table, typename Db, bool enabled>
void IRdbTableModelInterface<T, Table, Db, enabled>::truncateTable()
{
    auto query = this->createQuery(this->m_dialect.truncateTableSql(tableInfo()));
    query.exec();
}

template<typename T, typename Table, typename Db, bool enabled>
bool IRdbTableModelInterface<T, Table, Db, enabled>::containsTable(const QString &tableName)
{
    QStringList tables = this->m_database.getRdbTables();
    for(const QString& table : tables){
        if(tableName.compare( table, Qt::CaseInsensitive) == 0){
            return true;
        }
    }
    return false;
}

template<typename T, typename Table, typename Db, bool enabled>
inline const IRdbTableInfo &IRdbTableModelInterface<T, Table, Db, enabled>::tableInfo() const
{
    return Table::staticEntityInfo();
}

template<typename T, typename Table, typename Db, bool enabled>
double IRdbTableModelInterface<T, Table, Db, enabled>::$order() const
{
    return 50;
}

template<typename T, typename Table, typename Db, bool enabled>
void IRdbTableModelInterface<T, Table, Db, enabled>::$task()
{
    if /*constexpr*/ (enabled){
        QString name = tableInfo().m_entityName;
        if(containsTable(name)){
//            Db::instance().dropTable(tableInfo());
//            qDebug().noquote() << QString::fromStdString(m_database.getClassName()) << "EXIST TABLE: " << name;
            return;
        }

        createTable();
        if(containsTable(name)){
            qDebug().noquote() << IMetaUtil::getTypeName<T>() << "CREATE TABLE: " << name;
        }else{
            qDebug().noquote() << IMetaUtil::getTypeName<T>() << "CREATE TABLE: " << name << "FAILED";
        }
    }
}

template<typename T, typename Table, typename Db, bool enabled>
typename IRdbTableModelInterface<T, Table, Db, enabled>::IRdbTableModelInterfaceInitPrivate
    IRdbTableModelInterface<T, Table, Db, enabled>::m_private;

template<typename T, typename Table, typename Db, bool enabled>
IRdbTableModelInterface<T, Table, Db, enabled>::IRdbTableModelInterfaceInitPrivate::IRdbTableModelInterfaceInitPrivate()
{
    if constexpr (enabled){
        static std::once_flag flag;
        std::call_once(flag, [](){
            ITaskManage::instance().addTaskWare(&ISolo<T>());
        });
    }
}

$PackageWebCoreEnd

#endif
