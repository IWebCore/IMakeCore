#pragma once

#include "core/util/IHeaderUtil.h"
#include "core/config/IProfileImport.h"

namespace asio {
    namespace ssl {
        class context;
    }
}

$PackageWebCoreBegin
class ITcpServer
{
public:
    ITcpServer(asio::io_context& context);
    virtual ~ITcpServer();

public:
    void listen();

#ifdef IWEBCORE_ENABLE_SSL
    void setSslContext(asio::ssl::context* context);
#endif

private:
    void loadResolverFactory();
    void doAccept();

private:
    void doAcceptTcp();

#ifdef IWEBCORE_ENABLE_SSL
    void doAcceptTcps();
#endif

private:
    bool filterSocket(asio::ip::tcp::socket& socket);

protected:
    std::string m_ip{};
    int m_port{};
    int m_resolverFactoryId{-1};
    asio::io_context& m_context;
    asio::ip::tcp::acceptor* m_acceptor{};

private:
    bool m_isSsl{false};
#ifdef IWEBCORE_ENABLE_SSL
    asio::ssl::context* m_sslContext{};
#endif
};

$PackageWebCoreEnd
