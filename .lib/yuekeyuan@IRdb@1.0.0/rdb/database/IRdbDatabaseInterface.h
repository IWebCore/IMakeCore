#pragma once

#include "core/util/IHeaderUtil.h"
#include "core/task/unit/ITaskWareUnit.h"
#include "core/unit/ISoloUnit.h"
#include "rdb/IRdbAbort.h"
#include "rdb/IRdbCatagory.h"
#include "rdb/database/IRdbDatabaseWare.h"

$PackageWebCoreBegin

// TODO: 所有的 DataBase 都要做 flatten, 防止编译问题。
template<typename T, typename Dialect, bool enabled = true>
class IRdbDatabaseInterface
    : public IRdbDatabaseWare, public ITaskWareUnit<T, IRdbCatagory>, public ISoloUnit<T>
{
public:
    using DialectType = Dialect;

public:
    IRdbDatabaseInterface();

public:
    virtual double $order() const final;
    virtual void $task() override;
};

template<typename T, typename Dialect, bool enabled>
IRdbDatabaseInterface<T, Dialect, enabled>::IRdbDatabaseInterface()
    : IRdbDatabaseWare(Dialect::instance())
{
}

template<typename T, typename Dialect, bool enabled>
double IRdbDatabaseInterface<T, Dialect, enabled>::$order() const
{
    return 0;
}

template<typename T, typename Dialect, bool enabled>
void IRdbDatabaseInterface<T, Dialect, enabled>::$task()
{
    if constexpr (enabled) {
        static std::once_flag flag;
        std::call_once(flag, [](){
            IRdbDatabaseInterface<T, Dialect, enabled>& ware = T::instance();
            ware.m_dataSource = ware.getDataSource();
            ware.m_connectionTrait = ware.getConnectionTrait();
            if(!QSqlDatabase::drivers().contains(ware.m_dataSource.driverName)){
                QString tip = QString("sql driver not exist, DriverName: ").append(ware.m_dataSource.driverName);
                IRdbAbort::abortDataSourceError(tip, $ISourceLocation);
            }

            const auto& trait = ware.m_connectionTrait;
            for(int index=0; index< trait.minConnection; index++){
                ware.m_connections.push_back(ware.createConnection());
            }
            ware.createWatchTimer();
        });
    }
}

$PackageWebCoreEnd
