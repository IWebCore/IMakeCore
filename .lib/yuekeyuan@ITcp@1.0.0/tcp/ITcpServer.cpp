#include "ITcpServer.h"
#include "core/config/IProfileImport.h"
#include "core/config/IContextManage.h"
#include "tcp/ITcpAbort.h"
#include "tcp/ITcpConnection.h"
#include "tcp/ITcpManage.h"
#include "tcp/ITcpSocketFilterInterface.h"
#include "tcp/ITcpSocket.h"

$PackageWebCoreBegin

ITcpServer::ITcpServer(asio::io_context& context)
    : m_context(context)
{
    m_ip = *$StdString{"/tcp/ip", "127.0.0.1"};
    m_port = *$Int{"/tcp/port", 8550};
    m_acceptor = new asio::ip::tcp::acceptor(m_context);
}

ITcpServer::~ITcpServer()
{
    if(m_acceptor){
        if(m_acceptor->is_open()){
            m_acceptor->close();
        }

        delete m_acceptor;
        m_acceptor = nullptr;
    }
}

void ITcpServer::listen()
{
    if(m_acceptor->is_open()){
        qFatal("server started already");
    }

    loadResolverFactory();

    asio::ip::tcp::resolver resolver(m_context);
    asio::ip::tcp::endpoint endpoint = *resolver.resolve(
                m_ip, std::to_string(m_port)).begin();
    m_acceptor->open(endpoint.protocol());
    m_acceptor->set_option(asio::ip::tcp::acceptor::reuse_address(true));
    m_acceptor->bind(endpoint);
    m_acceptor->listen(SOMAXCONN);
    doAccept();

    IContextManage::instance().addConfig(IJson(m_ip), "/runtime/tcp/ip");
    IContextManage::instance().addConfig(IJson(m_port), "/runtime/tcp/port");
    IContextManage::instance().addConfig(IJson(m_isSsl), "runtime/tcp/ssl");
    qDebug() << "server started, listen at " << QString::fromStdString(m_ip) + ":" + QString::number(m_port);
}

#ifdef IWEBCORE_ENABLE_SSL
void ITcpServer::setSslContext(asio::ssl::context *context)
{
    m_isSsl = true;
    m_sslContext = context;
}
#endif

void ITcpServer::loadResolverFactory()
{
    if(m_resolverFactoryId >= 0){
        return;
    }
    $StdString factory{"/tcp/resolverFactory"};
    IString data(&(*factory));
    m_resolverFactoryId = ITcpManage::instance().getResolverFactoryId(data);
    if(m_resolverFactoryId == -1){
        ITcpAbort::abortResolverFactoryNotRegistered("lack tcp resolver factory", $ISourceLocation);
    }
}

void ITcpServer::doAccept()
{
#ifdef IWEBCORE_ENABLE_SSL
    if(m_isSsl){
        return doAcceptTcps();
    }
#endif
    return doAcceptTcp();
}

void ITcpServer::doAcceptTcp()
{
    m_acceptor->async_accept(
        [this](std::error_code ec, asio::ip::tcp::socket socket){
            if(!ec && !filterSocket(socket)){
                auto connection = new ITcpConnection(new ITcpSocket(std::move(socket)), m_resolverFactoryId);
                Q_UNUSED(connection)
            }
            doAcceptTcp();
        }
    );
}

#ifdef IWEBCORE_ENABLE_SSL
void ITcpServer::doAcceptTcps()
{
    m_acceptor->async_accept([this](std::error_code ec, asio::ip::tcp::socket socket){
        if(!ec && !filterSocket(socket)){
            auto ssocket = new asio::ssl::stream<asio::ip::tcp::socket>(std::move(socket), *m_sslContext);
            ssocket->async_handshake(asio::ssl::stream_base::server,
               [this, ssocket](const asio::error_code& error) {
                   if (!error) {
                       auto connection = new ITcpConnection(new ITcpSocket(ssocket), m_resolverFactoryId);
                       Q_UNUSED(connection)
                   }else{
                       qDebug() << QString::fromStdString(error.message());
                       delete ssocket;
                   }
               }
            );
        }
        doAcceptTcps();
    });
}
#endif

bool ITcpServer::filterSocket(asio::ip::tcp::socket &socket)
{
    static const auto& s_filters = ITcpManage::instance().getIpFilterWares();
    static bool s_enabled = !s_filters.empty();
    if(s_enabled){
        for(auto filter : s_filters){
            if(!filter->filter(socket)){
                socket.close();
                return true;
            }
        }
    }

    $Int m_timeout{"/http/readTimeOut", 30*1000};   // ms

#if defined(_WIN32) || defined(WIN32)
    socket.set_option(asio::detail::socket_option::integer<SOL_SOCKET, SO_RCVTIMEO>{ *m_timeout });
#else
    struct timeval tv;
    tv.tv_sec = *m_timeout / 1000;          // Seconds
    tv.tv_usec = ((*m_timeout) % 1000) * 1000; // Microseconds
    setsockopt(
        socket.native_handle(),
        SOL_SOCKET,
        SO_RCVTIMEO,
        &tv,
        sizeof(tv)
    );
#endif

    return false;
}

$PackageWebCoreEnd
