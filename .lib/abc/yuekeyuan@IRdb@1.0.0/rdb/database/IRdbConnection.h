#pragma once

#include "core/util/IHeaderUtil.h"

$PackageWebCoreBegin

class IRdbDatabaseWare;
class IRdbConnection
{
public:
    explicit IRdbConnection(IRdbDatabaseWare& ware, QSqlDatabase db);
    ~IRdbConnection();

public:
    void releaseConnection();
    bool isExpired(int second) const;

public:
    IRdbDatabaseWare& m_databaseWare;
    QSqlDatabase m_database;

public:
    int64_t m_createTime;
    int64_t m_lastUseTime;
    std::size_t m_useCount{};
};

$PackageWebCoreEnd
