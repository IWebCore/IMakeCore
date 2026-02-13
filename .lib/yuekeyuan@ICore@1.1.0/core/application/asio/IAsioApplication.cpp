#if __has_include(<asio.hpp>)

#include "IAsioApplication.h"
#include "core/application/asio/IAsioContext.h"
#include "core/config/IContextImport.h"

#ifdef _WIN32
#include <windows.h>
#endif

$PackageWebCoreBegin

IAsioApplication::IAsioApplication()
{
}

IHandle IAsioApplication::startTimer(std::chrono::milliseconds duration, TaskType task)
{
    return IAsioContext::startTimer(duration, task);
}

void IAsioApplication::stopTimer(IHandle handle)
{
    return IAsioContext::stopTimer(handle);
}

void IAsioApplication::post(TaskType task)
{
    IAsioContext::post(task);
}

int IAsioApplication::exec()
{
    IAsioContext::instance();
    startTimer(std::chrono::seconds(1), [&](){
        m_time = std::chrono::duration_cast<std::chrono::nanoseconds>(std::chrono::high_resolution_clock().now().time_since_epoch()).count();
    });

    std::thread thread([&](){
        $ContextInt count{"/system/threadCount", static_cast<int>(std::thread::hardware_concurrency() * 2)};
        IAsioContext::instance().run(*count);
    });
    thread.detach();

    return m_qCoreApplication->exec();
    return 0;
}

QString IAsioApplication::applicationType() const
{
    return "asio";
}

$PackageWebCoreEnd

#endif
