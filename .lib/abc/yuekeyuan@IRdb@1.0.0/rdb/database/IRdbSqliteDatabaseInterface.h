#pragma once

#include "rdb/database/IRdbDatabaseInterface.h"
#include "rdb/dialect/IRdbSqliteDialect.h"
#include "rdb/exception/IRdbException.h"

$PackageWebCoreBegin

template<typename T, bool enabled = true>
class IRdbSqliteDatabaseInterface : public IRdbDatabaseInterface<T, IRdbSqliteDialect, enabled>
{
public:
    IRdbSqliteDatabaseInterface() = default;

public:
    virtual IRdbConnectionTrait getConnectionTrait() const override;
    virtual QSqlDatabase openDatatbase() override;

public:
    virtual void $task() final;
};

template<typename T, bool enabled>
IRdbConnectionTrait IRdbSqliteDatabaseInterface<T, enabled>::getConnectionTrait() const
{
    IRdbConnectionTrait trait;
    trait.maxConnection = 1;
    return trait;
}

template<typename T, bool enabled>
QSqlDatabase IRdbSqliteDatabaseInterface<T, enabled>::openDatatbase()
{
    QSqlDatabase database;
    database = QSqlDatabase::addDatabase(this->m_dataSource.driverName, IMetaUtil::getTypeName<T>() + "_0");
    database.setDatabaseName(this->m_dataSource.databaseName);

    if(!database.open()){
        throw IRdbException(database.lastError());
    }

    return database;
}

template<typename T, bool enabled>
void IRdbSqliteDatabaseInterface<T, enabled>::$task()
{
    if constexpr (enabled) {
        static std::once_flag flag;
        std::call_once(flag, [=](){

            // IRdbDatabaseInterface<T, IRdbSqliteDialect, enabled>& ware = T::instance();
            // ware.m_dataSource = ware.getDataSource();
            // ware.m_connectionTrait = ware.getConnectionTrait();
            std::thread thread([=](){
                this->m_dataSource = this->getDataSource();
                this->m_connectionTrait = this->getConnectionTrait();
                if(!QSqlDatabase::drivers().contains(this->m_dataSource.driverName)){
                    QString tip = QString("sql driver not exist, DriverName: ").append(/*ware.*/this->m_dataSource.driverName);
                    IRdbAbort::abortDataSourceError(tip, $ISourceLocation);
                }

                // const auto& trait = /*ware.*/m_connectionTrait;
                for(int index=0; index< this->m_connectionTrait.minConnection; index++){
                    /*ware.*/this->m_connections.push_back(/*ware.*/this->createConnection());
                }
                // /*ware.*/this->createWatchTimer();

            });
            thread.join();
        });
    }
}

$PackageWebCoreEnd
