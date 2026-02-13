#include "IRdbDatabaseWare.h"
#include "core/application/iApp.h"
#include "rdb/exception/IRdbException.h"
#include "rdb/entity/IRdbTableInfo.h"
#include "rdb/entity/IRdbViewInfo.h"
#include "rdb/dialect/IRdbDialectWare.h"
#include "rdb/database/IRdbConnection.h"
#include "rdb/database/IRdbConnectionTrait.h"

$PackageWebCoreBegin

IRdbDatabaseWare::IRdbDatabaseWare(const IRdbDialectWare & dialect)
    : m_dialect(dialect)
{
}

IRdbDatabaseWare::~IRdbDatabaseWare()
{
    if(m_timerId){
        iApp->stopTimer(m_timerId);
        m_timerId = 0;
    }

    std::lock_guard lock(m_connectionMutex);
    if(static_cast<int>(m_connections.size()) != m_connectionCount){  // NOTE: 有的资源释放出去了，没有回收，怎么办
        qWarning() << "NOT ALL Database released";
    }
    while(!m_connections.empty()){
        destroyConnection(m_connections.front());
        m_connections.pop_front();
    }
}

ISqlQuery IRdbDatabaseWare::createQuery()
{
    if(auto db = lockConnection()){
        return ISqlQuery(db, m_dialect);
    }
    throw IRdbException("fail to create query");
}


IRdbConnection *IRdbDatabaseWare::lockConnection()
{
    std::unique_lock lock(m_connectionMutex);

    if(!m_connections.empty()){
        auto front = m_connections.front();
        m_connections.pop_front();
        return front;
    }

    if(m_connectionCount < m_connectionTrait.maxConnection){
        return createConnection();
    }

    if(m_connectionCv.wait_for(lock, std::chrono::seconds(m_connectionTrait.connectionTimeout), [&](){
            return !m_connections.empty();
        })){
        auto front = m_connections.front();
        m_connections.pop_front();
        return front;
    }
    throw IRdbException("lockDatabase error");
}

void IRdbDatabaseWare::unlockConnection(IRdbConnection *db)
{
    std::lock_guard lock(m_connectionMutex);
    m_connections.push_back(db);
    m_connectionCv.notify_one();
}


QStringList IRdbDatabaseWare::getRdbTables()
{
    auto db = lockConnection();
    if(!db){
        throw IRdbException("lock database failed");
    }
    QStringList names = db->m_database.tables(QSql::Tables);
    unlockConnection(db);
    return names;
}

QStringList IRdbDatabaseWare::getRdbViews()
{
    auto db = lockConnection();
    if(!db){
        throw IRdbException("lock database failed");
    }

    QStringList names = db->m_database.tables(QSql::Views);
    unlockConnection(db);
    return names;
}

void IRdbDatabaseWare::dropTable(const IRdbTableInfo &table)
{
    auto query = createQuery();
    query.exec(m_dialect.dropTableSql(table));
}

void IRdbDatabaseWare::dropView(const IRdbViewInfo &view)
{
    auto query = createQuery();
    query.exec(m_dialect.dropViewSql(view));
}

IRdbConnectionTrait IRdbDatabaseWare::getConnectionTrait() const
{
    IRdbConnectionTrait trait;
    return trait;
}

IRdbConnection *IRdbDatabaseWare::createConnection()
{
    auto db = new IRdbConnection((*this), openDatatbase());
    m_connectionCount ++;
    return db;
}

void IRdbDatabaseWare::destroyConnection(IRdbConnection *db)
{
    m_connectionCount --;
    delete db;
}

void IRdbDatabaseWare::timerTask()
{
    std::lock_guard lock(m_connectionMutex);
    if(m_connectionCount == m_connectionTrait.minConnection){
        return;
    }

    if(m_connectionCount < m_connectionTrait.minConnection){
        int count = m_connectionTrait.minConnection - m_connectionCount;
        for(int i=0; i<count; i++){
            m_connections.push_back(createConnection());
        }
        return; // 创建 connection
    }

    for(int index=static_cast<int>(m_connections.size()) -1; index > m_connectionTrait.minConnection; index--){
        auto connection = *(std::next(m_connections.begin(), index));
        if(connection->isExpired(m_connectionTrait.idleTimeout)){
            m_connections.remove(connection);
            delete connection;
        }
    }
}

void IRdbDatabaseWare::createWatchTimer()
{
    m_timerId = iApp->startTimer( std::chrono::seconds(m_connectionTrait.timerDuration),
        [=](){
            try{
                timerTask();
            }catch(const IRdbException& exception){
                qWarning() << exception.getCause();
            }
        }
    );
}

$PackageWebCoreEnd
