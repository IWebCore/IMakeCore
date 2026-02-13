#pragma once

#include "core/util/IHeaderUtil.h"
#include "core/base/IString.h"

$PackageWebCoreBegin

class IException
{
public:
    IException(QString cause);
    virtual ~IException() = default;

public:
    const QString& getCause() const;

private:
    QString m_cause;
};

$PackageWebCoreEnd
