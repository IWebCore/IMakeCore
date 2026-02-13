#pragma once

#include "core/util/IHeaderUtil.h"
#include "core/base/IException.h"

$PackageWebCoreBegin

class IRdbException : public IException
{
public:
    IRdbException(const QSqlError& error);
    IRdbException(const QString& exception);
};

inline IRdbException::IRdbException(const QSqlError& error)
    : IException(error.text())
{
}

inline IRdbException::IRdbException(const QString &exception)
    : IException(exception)
{
}

$PackageWebCoreEnd
