#if __has_include(<asio.hpp>)

#include "IAsioTimer.h"
#include "core/application/asio/IAsioContext.h"

$PackageWebCoreBegin

IAsioTimer::IAsioTimer(std::chrono::milliseconds duration, IAsioTimer::Task task)
    : m_duration(duration), m_task(std::move(task)), m_timer(IAsioContext::instance().getContext())
{
    startTimer();
}

IAsioTimer::~IAsioTimer()
{
    m_timer.cancel();
}

void IAsioTimer::cancelTimer()
{
    m_timer.cancel();
    m_isContinue = false;
}

void IAsioTimer::startTimer()
{
    m_timer.expires_after(m_duration);
    m_timer.async_wait([=](std::error_code err){
        if(err){
            return;
        }

        m_task();

        if(m_isContinue){
            startTimer();
        }
    });
}

$PackageWebCoreEnd

#endif
