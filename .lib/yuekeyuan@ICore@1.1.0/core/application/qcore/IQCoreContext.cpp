#include "IQCoreContext.h"

#include "core/application/qcore/IQCoreTimer.h"

$PackageWebCoreBegin

IQCoreContext::~IQCoreContext()
{
    for(auto timer : m_timers){
        timer->cancelTimer();
        delete timer;
    }
    m_timers.clear();
}

void IQCoreContext::post(Task task)
{
    QTimer::singleShot(0, task);
}

IHandle IQCoreContext::startTimer(std::chrono::milliseconds duration, IQCoreContext::Task task)
{
    auto timer = new IQCoreTimer(duration, task);
    instance().m_timers.append(timer);
    return timer->timerId();
}

void IQCoreContext::stopTimer(IHandle handle)
{
    for(auto timer : instance().m_timers){
        if(timer->timerId() == handle){
            instance().m_timers.removeOne(timer);
            timer->cancelTimer();
            delete timer;
            return;
        }
    }
}

$PackageWebCoreEnd
