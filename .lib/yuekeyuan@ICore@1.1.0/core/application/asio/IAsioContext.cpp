#if __has_include(<asio.hpp>)

#include "IAsioContext.h"
#ifdef __clang__
    #include "core/application/qcore/IQCoreContext.h"
#else
    #include "core/application/asio/IAsioTimer.h"
#endif

$PackageWebCoreBegin

IAsioContext::IAsioContext()
{

}

IAsioContext::~IAsioContext()
{
#ifndef __clang__
    for(auto timer : m_timers){
        delete timer;
    }
    m_timers.clear();
#endif
}

asio::io_context &IAsioContext::getContext()
{
    return m_context;
}

void IAsioContext::run(int threadCount)
{
    std::vector<std::thread> threads;
    for(int i=0; i<threadCount; i++){
        threads.emplace_back(std::thread([&](){
            m_context.run();
        }));
    }
    for(int i=0; i<threadCount; i++){
        threads[i].join();
    }
}

void IAsioContext::post(IAsioContext::Task task)
{
    instance().m_context.post(task);
}

// see: https://github.com/chriskohlhoff/asio/issues/1646
IHandle IAsioContext::startTimer(std::chrono::milliseconds duration, IAsioContext::Task task)
{
#ifdef __clang__
    return IQCoreContext::instance().startTimer(duration, task);
#else
    auto timer = new IAsioTimer(duration, task);
    instance().m_timers.append(timer);
    return reinterpret_cast<IHandle>(timer);
#endif
}

void IAsioContext::stopTimer(IHandle ptr)
{
#ifdef __clang__
    return IQCoreContext::stopTimer(ptr);
#else
    for(auto& timer : instance().m_timers){
        if(ptr == reinterpret_cast<IHandle>(timer)){
            instance().m_timers.removeOne(timer);
            timer->cancelTimer();
            delete timer;
            return;
        }
    }
#endif
}

$PackageWebCoreEnd

#endif
