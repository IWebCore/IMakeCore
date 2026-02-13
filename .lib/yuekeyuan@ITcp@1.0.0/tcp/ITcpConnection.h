#pragma once

#include "core/util/IHeaderUtil.h"
#include <queue>

$PackageWebCoreBegin

class ITcpSocket;
class ITcpResolver;
class ITcpConnection
{
    friend class ITcpResolver;
public:
    ITcpConnection(ITcpSocket* socket, int resolverFactoryId);
    virtual ~ITcpConnection();

public:
    void doReadBy(std::size_t length);
    void doReadDataBy(std::size_t length);
    void doReadStreamBy(std::size_t length);

    void doReadUtil(IStringView, std::size_t startPos = 0);
    void doReadDataUtil(IStringView, std::size_t startPos = 0);
    void doReadStreamUntil(IStringView, std::size_t startPos = 0);

    void doWrite(ITcpResolver*);

    void doReadFinished();
    void doWriteFinished();
    void doReadError(std::error_code);
    void doWriteError(std::error_code);

public:
    std::string remoteIp() const;

private:
    void startReadData();

private:
    void doWriteImpl();
    void readDataUntilHandler(IStringView view, std::size_t startPos, std::error_code error, std::size_t byteRead);

public:
    std::atomic_bool m_keepAlive{false};
    std::atomic_int m_addResolverCount{};
    std::atomic_int m_deleteResolverCount{};

private:
    std::mutex m_mutex;
    std::atomic_int m_unWrittenCount{0};
    ITcpSocket* m_socket;
    std::list<ITcpResolver*> m_resolvers;
    int m_resolverFactoryId;
};

$PackageWebCoreEnd
