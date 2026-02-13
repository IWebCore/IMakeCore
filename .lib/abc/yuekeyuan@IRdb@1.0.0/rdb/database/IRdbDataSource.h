#pragma once

#include "core/bean/IBeanInterface.h"

$PackageWebCoreBegin

class IRdbDataSource : public IBeanInterface<IRdbDataSource>
{
    Q_GADGET
public:
    IRdbDataSource();
    static IRdbDataSource fromConfig(const std::string&);

public:
    $BeanFieldRequired(driverName)
    $BeanFieldDeclare(QString, driverName)
    QString driverName;

    $BeanFieldRequired(databaseName)
    $BeanFieldDeclare(QString, databaseName)
    QString databaseName;

    $BeanFieldDeclare(QString, host)
    QString host;

    $BeanFieldDeclare(QString, user)
    QString user;

    $BeanFieldDeclare(QString, password)
    QString password;

    $BeanFieldDeclare(int, port)
    int port{-1};
};

extern template class IBeanInterface<IRdbDataSource>;

$PackageWebCoreEnd

