#include "IException.h"

$PackageWebCoreBegin

IException::IException(QString cause)
    : m_cause(std::move(cause))
{
}

const QString &IException::getCause() const
{
    return m_cause;
}

$PackageWebCoreEnd
