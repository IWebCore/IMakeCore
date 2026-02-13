#include "IApplicationWare.h"
#include "core/task/ITaskManage.h"

$PackageWebCoreBegin

QString IApplicationWare::applicationName() const
{
    return qApp->applicationName();
}

QString IApplicationWare::applicationPath() const
{
    return qApp->applicationFilePath();
}

QString IApplicationWare::workingDirectory() const
{
    return QDir::currentPath();
}

QStringList IApplicationWare::arguments() const
{
    return m_arguments;
    // return m_qCoreApplication->arguments();
}

IApplicationWare *IApplicationWare::invoke(int argc, char ** argv)
{
    static QCoreApplication qCoreApp(argc, argv);
    m_arguments = qCoreApp.arguments();
    m_qCoreApplication = &qCoreApp;
    return this;
}

$PackageWebCoreEnd
