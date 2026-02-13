#pragma once

#if __has_include(<QGuiApplication>)

#include "core/application/IApplicationInterface.h"

$PackageWebCoreBegin

    class IQGuiApplication : public IApplicationInterface<IQGuiApplication>
{
public:
    IQGuiApplication();

public:
    virtual IHandle startTimer(std::chrono::milliseconds duration, TaskType task) final;
    virtual void stopTimer(IHandle) final;
    virtual void post(TaskType) final;

public:
    virtual int exec() final;

protected:
    virtual QString applicationType() const final;
    virtual IApplicationWare* invoke(int argc, char ** argv) final;
};

$PackageWebCoreEnd

#endif
