#pragma once

#include "core/util/IHeaderUtil.h"
#include "core/base/IHandle.h"

$PackageWebCoreBegin

class IQCoreTimer : public QObject
{
    Q_OBJECT
public:
    using Task = std::function<void()>;

public:
    IQCoreTimer(std::chrono::milliseconds duration, Task);
    ~IQCoreTimer() = default;

public:
    void cancelTimer();
    void startTimer();
    IHandle timerId() const;

protected:
    virtual void timerEvent(QTimerEvent *event) final;

private:
    std::chrono::milliseconds m_duration;
    Task m_task;
    QBasicTimer m_timer;
};

$PackageWebCoreEnd
