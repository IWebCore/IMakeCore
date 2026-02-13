#pragma once

#include "core/util/IHeaderUtil.h"
#include "core/task/unit/ITaskInstantUnit.h"
#include "ITcpResolverFactoryWare.h"
#include "tcp/ITcpManage.h"

$PackageWebCoreBegin

template<typename T, typename U, bool enabled=true>
class ITcpResolverFactoryInterface : public ITcpResolverFactoryWare, public ITaskInstantUnit<T, enabled>
{
public:
    virtual void $task() final;
    virtual ITcpResolver* createResolver(ITcpConnection&, int) final;
    virtual void destroyResolver(ITcpResolver*) final;
};

template<typename T, typename U, bool enabled>
void ITcpResolverFactoryInterface<T, U, enabled>::$task()
{
    if constexpr (enabled){
        ITcpManage::instance().registResolverFactory(&ISolo<T>());
    }
}

template<typename T, typename U, bool enabled>
ITcpResolver *ITcpResolverFactoryInterface<T, U, enabled>::createResolver(ITcpConnection &connection, int id)
{
    return new U(connection, id);
}

template<typename T, typename U, bool enabled>
void ITcpResolverFactoryInterface<T, U, enabled>::destroyResolver(ITcpResolver *resolver)
{
    delete resolver;
}

$PackageWebCoreEnd
