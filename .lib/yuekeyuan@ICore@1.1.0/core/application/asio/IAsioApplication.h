#pragma once

#if __has_include(<asio.hpp>)

#include "core/application/IApplicationInterface.h"

$PackageWebCoreBegin

class IAsioApplication : public IApplicationInterface<IAsioApplication>
{
public:
    IAsioApplication();

public:
    virtual IHandle startTimer(std::chrono::milliseconds duration, TaskType task) final;
    virtual void stopTimer(IHandle) final;
    virtual void post(TaskType) final;

public:
    virtual int exec() final;

protected:
    virtual QString applicationType() const final;
};

$PackageWebCoreEnd

#endif
