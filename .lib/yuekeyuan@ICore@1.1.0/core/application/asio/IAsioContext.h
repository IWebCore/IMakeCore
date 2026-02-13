#pragma once

#if __has_include(<asio.hpp>)

#include "core/unit/ISoloUnit.h"
#include "core/base/IHandle.h"

$PackageWebCoreBegin

class IAsioTimer;
class IAsioContext : public ISoloUnit<IAsioContext>
{
public:
    using Task = std::function<void()>;

public:
    IAsioContext();
    ~IAsioContext();

public:
    asio::io_context& getContext();

    void run(int threadCount);

public:
    static void post(Task);
    static IHandle startTimer(std::chrono::milliseconds duration, Task);
    static void stopTimer(IHandle ptr);

private:
    asio::io_context m_context;
    QList<IAsioTimer*> m_timers;
};

$PackageWebCoreEnd

#endif
