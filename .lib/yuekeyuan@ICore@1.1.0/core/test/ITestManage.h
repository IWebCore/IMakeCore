#pragma once

#include "core/util/IHeaderUtil.h"
#include <core/unit/ISoloUnit.h>

$PackageWebCoreBegin

class ITestManage : public ISoloUnit<ITestManage>
{
public:
    ITestManage() = default;

public:
    void addTest(const QString& type, QObject* obj);
    bool hasTests(const QString&) const;
    void invokeTests(const QString& type);

private:
    QMap<QString, QList<QObject*>> m_testCases;
};

$PackageWebCoreEnd
