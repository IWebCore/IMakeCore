#if __has_include(<QGuiApplication>)

#if __has_include(<QApplication>)
#include <QApplication>
#endif

#include <QGuiApplication>
#include "IQGuiApplication.h"
#include "core/application/qcore/IQCoreContext.h"
#include "core/task/ITaskManage.h"

$PackageWebCoreBegin

IQGuiApplication::IQGuiApplication()
{
}

IHandle IQGuiApplication::startTimer(std::chrono::milliseconds duration, TaskType task)
{
    return IQCoreContext::startTimer(duration, task);
}

void IQGuiApplication::stopTimer(IHandle handle)
{
    return IQCoreContext::stopTimer(handle);
}

void IQGuiApplication::post(TaskType task)
{
    return IQCoreContext::post(task);
}

int IQGuiApplication::exec()
{
    startTimer(std::chrono::seconds(1), [&](){
        m_time = std::chrono::duration_cast<std::chrono::nanoseconds>(std::chrono::high_resolution_clock().now().time_since_epoch()).count();
    });
    return qApp->exec();
}

QString IQGuiApplication::applicationType() const
{
    return "QGui";
}

IApplicationWare* IQGuiApplication::invoke(int argc, char ** argv)
{
#if __has_include(<QApplication>)
    static QApplication app(argc, argv);
#else
    static QGuiApplication app(argc, argv);
#endif
    return this;
}

$PackageWebCoreEnd

#endif
