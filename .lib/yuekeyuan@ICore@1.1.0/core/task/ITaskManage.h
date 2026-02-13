#pragma once

#include "core/util/IHeaderUtil.h"
#include "core/util/IPreProcessorUtil.h"
#include "core/unit/ISoloUnit.h"

$PackageWebCoreBegin

class ITaskWare;
class ITaskCatagory;

class ITaskManage : public ISoloUnit<ITaskManage>
{
public:
    using FunType = std::function<void()>;
    using ArgumentTaskFunType = std::function<void(const QStringList&)>;

public:
    static void run();

    void addTaskWare(ITaskWare* node);
    void addTaskCatagory(ITaskCatagory*);

private:
    void invokeTaskCatagories();

private:
    void checkCatagoryExceed();
    void checkTaskExceed();
    void mergeTasksToCatagories();
    void execCatagories();

private:
    QList<ITaskWare*> m_taskWares;
    QList<ITaskCatagory*> m_catagories;
    bool m_isTaskFinished{false};
};

$PackageWebCoreEnd
