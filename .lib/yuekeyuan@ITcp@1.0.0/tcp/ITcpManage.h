#pragma once

#include "core/util/IHeaderUtil.h"
#include "core/unit/ISoloUnit.h"
#include "tcp/ITcpResolverFactoryWare.h"
#include <unordered_set>


$PackageWebCoreBegin

class ITcpSocketFilterWare;
class ITcpConnection;
class ITcpManage : public ISoloUnit<ITcpManage>
{
public:
    ITcpManage() = default;

//public:
//    void addConnection(ITcpConnection*);
//    void removeConnection(ITcpConnection*);

public:
    void registResolverFactory(ITcpResolverFactoryWare*);
    int getResolverFactoryId(const IString&);
    ITcpResolver* createResolver(ITcpConnection&, int id);
    void destoryResolver(ITcpResolver*);

    void registIpFilterWare(ITcpSocketFilterWare*);
    std::vector<ITcpSocketFilterWare*> getIpFilterWares();


private:
    std::vector<ITcpResolverFactoryWare*> m_resolverFactories;
    std::vector<ITcpSocketFilterWare*> m_ipFilterWare;
};

$PackageWebCoreEnd
