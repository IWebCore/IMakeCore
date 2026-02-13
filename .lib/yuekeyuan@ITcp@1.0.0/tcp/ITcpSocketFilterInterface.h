#pragma once

#include "core/util/IHeaderUtil.h"
#include "core/task/unit/ITaskWareUnit.h"
#include "core/unit/ISoloUnit.h"
#include "tcp/ITcpTaskCatagory.h"
#include "tcp/ITcpManage.h"

$PackageWebCoreBegin

class ITcpSocketFilterWare
{
public:
    virtual bool filter(asio::ip::tcp::socket& socket) = 0;
};

template<typename T, bool enabled = true>
class ITcpSocketFilterInterface : public ITcpSocketFilterWare, public ITaskWareUnit<T, ITcpTaskCatagory, enabled>, public ISoloUnit<T>
{
public:
    virtual void $task() final;
};

template<typename T, bool enabled>
void ITcpSocketFilterInterface<T, enabled>::$task()
{
    if (enabled){
        ITcpManage::instance().registIpFilterWare(&ISolo<T>());
    }
}

$PackageWebCoreEnd
