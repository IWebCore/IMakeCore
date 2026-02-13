#include "ITestManage.h"
#if __has_include(<QtTest>)
    #include <QtTest>
#endif

$PackageWebCoreBegin

void ITestManage::addTest(const QString &type, QObject *obj)
{
    instance().m_testCases[type].append(obj);
}

bool ITestManage::hasTests(const QString &type) const
{
    return instance().m_testCases.contains(type) && !instance().m_testCases[type].isEmpty();
}

void ITestManage::invokeTests(const QString &type)
{
#if __has_include(<QtTest>)
    auto& objs = instance().m_testCases[type];

    for(auto obj : objs){
        QTest::qExec(obj);
    }
#else
    Q_UNUSED(type)
    qFatal("Qt testlib do not configured, please configure Qt testlib in your configuration");
#endif
}

$PackageWebCoreEnd
