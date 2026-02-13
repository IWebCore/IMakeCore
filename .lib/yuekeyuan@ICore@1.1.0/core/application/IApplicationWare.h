#pragma once

#include "core/util/IHeaderUtil.h"
#include "core/base/IHandle.h"

$PackageWebCoreBegin

class IApplicationWare
{
public:
    using TaskType = std::function<void()>;

public:
    IApplicationWare() = default;
    virtual ~IApplicationWare() = default;

public:
    virtual QString applicationName() const;
    virtual QString applicationPath() const;
    virtual QString workingDirectory() const;
    virtual QStringList arguments() const;

public:
    virtual std::int64_t time() = 0;
    virtual IHandle startTimer(std::chrono::milliseconds duration, TaskType task) = 0;
    virtual void stopTimer(IHandle) = 0;
    virtual void post(TaskType) = 0;

public:
    virtual int exec() = 0;

protected:
    virtual QString applicationType() const = 0;
    virtual IApplicationWare* invoke(int, char**);

protected:
    QCoreApplication* m_qCoreApplication{};
    QStringList m_arguments;
};

$PackageWebCoreEnd
