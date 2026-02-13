#pragma once

#include "core/util/IHeaderUtil.h"
#include "core/base/IHandle.h"
#include "rdb/ISqlQuery.h"
#include "rdb/database/IRdbDataSource.h"
#include "rdb/database/IRdbConnectionTrait.h"
#include <QSqlDatabase>

$PackageWebCoreBegin

class IRdbDialectWare;
class IRdbConnection;
class IRdbTableInfo;
class IRdbViewInfo;

class IRdbDatabaseWare
{
    friend class IRdbConnection;
public:
    explicit IRdbDatabaseWare(const IRdbDialectWare&);
    virtual ~IRdbDatabaseWare();

public:
    virtual ISqlQuery createQuery();

public:
    virtual QStringList getRdbTables();
    virtual QStringList getRdbViews();
    virtual void dropTable(const IRdbTableInfo& table);
    virtual void dropView(const IRdbViewInfo& view);

public:
    virtual IRdbDataSource getDataSource() const = 0;
    virtual IRdbConnectionTrait getConnectionTrait() const;
    virtual QSqlDatabase openDatatbase() = 0;

    virtual IRdbConnection* lockConnection();
    virtual void unlockConnection(IRdbConnection*);
    IRdbConnection* createConnection();
    void destroyConnection(IRdbConnection* db);

    virtual void timerTask();
    void createWatchTimer();

public:
    const IRdbDialectWare& m_dialect;
    std::list<IRdbConnection*> m_connections;
    std::mutex m_connectionMutex;
    std::atomic<int> m_connectionCount{};
    std::condition_variable m_connectionCv;

public:
    IRdbDataSource m_dataSource{};
    IRdbConnectionTrait m_connectionTrait{};
    IHandle m_timerId{};
};

$PackageWebCoreEnd
