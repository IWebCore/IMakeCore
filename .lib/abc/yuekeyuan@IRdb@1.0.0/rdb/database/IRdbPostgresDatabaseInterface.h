#pragma once

#include "rdb/database/IRdbDatabaseInterface.h"
#include "rdb/dialect/IRdbPostgresDialect.h"
#include "rdb/exception/IRdbException.h"

$PackageWebCoreBegin

template<typename T, bool enabled = true>
class IRdbPostgresDatabaseInterface : public IRdbDatabaseInterface<T, IRdbPostgresDialect, enabled>
{
public:
    IRdbPostgresDatabaseInterface() = default;

public:
    virtual QSqlDatabase openDatatbase() override;
};

template<typename T, bool enabled>
QSqlDatabase IRdbPostgresDatabaseInterface<T, enabled>::openDatatbase()
{
    QSqlDatabase database = QSqlDatabase::addDatabase(this->m_dataSource.driverName, IMetaUtil::getTypeName<T>() + "_0");
    database.setDatabaseName(this->m_dataSource.databaseName);
    database.setHostName(this->m_dataSource.host);
    database.setUserName(this->m_dataSource.user);
    database.setPassword(this->m_dataSource.password);
    if(this->m_dataSource.port != -1){
        database.setPort(this->m_dataSource.port);
    }

    if(!database.open()){
        throw IRdbException(database.lastError());
    }

    return database;
}

$PackageWebCoreEnd
