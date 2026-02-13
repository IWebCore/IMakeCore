#pragma once

#include "core/application/IApplicationInterface.h"

$PackageWebCoreBegin

class IQCoreApplication : public IApplicationInterface<IQCoreApplication>
{
public:
    IQCoreApplication();

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
