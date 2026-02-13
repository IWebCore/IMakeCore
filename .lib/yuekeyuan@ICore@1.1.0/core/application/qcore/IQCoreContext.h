#pragma once

#include "core/unit/ISoloUnit.h"
#include "core/base/IHandle.h"

$PackageWebCoreBegin

class IQCoreTimer;
class IQCoreContext : public ISoloUnit<IQCoreContext>
{
public:
    using Task = std::function<void()>;

public:
    IQCoreContext() = default;
    ~IQCoreContext();

public:
    static void post(Task);
    static IHandle startTimer(std::chrono::milliseconds duration, Task);
    static void stopTimer(IHandle handle);

private:
    QList<IQCoreTimer*> m_timers;
};

$PackageWebCoreEnd
