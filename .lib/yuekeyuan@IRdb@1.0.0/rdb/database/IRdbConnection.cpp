#include "IRdbConnection.h"
#include "core/application/iApp.h"
#include "rdb/database/IRdbDatabaseWare.h"

$PackageWebCoreBegin

extern IApplicationWare* iApp;

IRdbConnection::IRdbConnection(IRdbDatabaseWare &ware, QSqlDatabase db)
    :m_databaseWare(ware), m_database(db)
{
    m_createTime = iApp->time();
    m_lastUseTime = iApp->time();
}

IRdbConnection::~IRdbConnection()
{
    m_database.close();
}

void IRdbConnection::releaseConnection()
{
    m_lastUseTime = iApp->time();
    m_useCount ++;
    m_databaseWare.unlockConnection(this);
}

bool IRdbConnection::isExpired(int second) const
{
    auto time = iApp->time();
    return (time - m_lastUseTime) > (int64_t)second * 1000000000;
}

$PackageWebCoreEnd
