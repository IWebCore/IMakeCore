#pragma once

#if __has_include(<asio.hpp>)

#include "core/util/IHeaderUtil.h"

$PackageWebCoreBegin

class IAsioTimer
{
public:
    using Task = std::function<void()>;

public:
    IAsioTimer(std::chrono::milliseconds duration, Task);
    ~IAsioTimer();

public:
    void cancelTimer();
    void startTimer();

private:
    std::chrono::milliseconds m_duration;
    Task m_task;
    asio::steady_timer m_timer;
    bool m_isContinue{true};
};

$PackageWebCoreEnd

#endif
