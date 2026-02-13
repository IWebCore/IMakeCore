#include "IQCoreTimer.h"

$PackageWebCoreBegin

IQCoreTimer::IQCoreTimer(std::chrono::milliseconds duration, IQCoreTimer::Task task)
    : QObject(), m_duration(duration), m_task(task)
{
    startTimer();
}

void IQCoreTimer::cancelTimer()
{
    m_timer.stop();
}

void IQCoreTimer::startTimer()
{
    m_timer.start(m_duration.count(), this);
}

IHandle IQCoreTimer::timerId() const
{
    return m_timer.timerId();
}

void IWebCore::IQCoreTimer::timerEvent(QTimerEvent *event)
{
    Q_UNUSED(event)

    m_task();
}

$PackageWebCoreEnd
