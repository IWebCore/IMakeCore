#include "IQCoreApplication.h"
#include "core/application/qcore/IQCoreContext.h"

$PackageWebCoreBegin

IQCoreApplication::IQCoreApplication()
{
}

IHandle IQCoreApplication::startTimer(std::chrono::milliseconds duration, TaskType task)
{
    return IQCoreContext::startTimer(duration, task);
}

void IQCoreApplication::stopTimer(IHandle handle)
{
    return IQCoreContext::stopTimer(handle);
}

void IQCoreApplication::post(TaskType task)
{
    return IQCoreContext::post(task);
}

int IQCoreApplication::exec()
{
    startTimer(std::chrono::seconds(1), [&](){
        m_time = std::chrono::duration_cast<std::chrono::nanoseconds>(std::chrono::high_resolution_clock().now().time_since_epoch()).count();
    });
    return qApp->exec();
}

QString IQCoreApplication::applicationType() const
{
    return "QCore";
}

$PackageWebCoreEnd
