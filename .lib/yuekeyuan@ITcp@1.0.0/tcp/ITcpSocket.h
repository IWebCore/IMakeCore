#pragma once

#include "core/util/IHeaderUtil.h"

#ifdef IWEBCORE_ENABLE_SSL
#include <asio/ssl.hpp>
#endif

$PackageWebCoreBegin

class ITcpSocket
{
public:
    using ISocket = asio::ip::tcp::socket;

#ifdef IWEBCORE_ENABLE_SSL
    using ISSocket = asio::ssl::stream<ISocket>;
#else
    using ISSocket = ISocket;
#endif

public:
    ITcpSocket(ISocket&& socket);
    ITcpSocket(ISSocket* ssocket);
    ~ITcpSocket();

public:
    bool is_open() const;
    void close();

    template<typename Condition, typename Token>
    void async_read(asio::mutable_buffers_1 buffer, Condition condition, Token&& token);

    template<typename Condition, typename Token>
    void async_read(asio::streambuf& buffer, Condition condition, Token&& token);

    template<typename Buffer, typename Token>
    void async_read_some(const Buffer& buffer, Token&& functor);

    template<typename Buffer, typename Token>
    void async_write(const Buffer& buffer, Token&&);

public:
    bool m_isSsl;
    ISSocket* m_ssocket{};
    ISocket * m_socket{};
};

template<typename Condition, typename Token>
void ITcpSocket::async_read(asio::mutable_buffers_1 buffer, Condition condition, Token&& token)
{
    if(!m_isSsl){
        asio::async_read(*m_socket, buffer, condition, std::move(token));
    }else{
        asio::async_read(*m_ssocket, buffer, condition, std::move(token));
    }
}

template<typename Condition, typename Token>
void ITcpSocket::async_read(asio::streambuf& buffer, Condition condition, Token&& token)
{
    if(!m_isSsl){
        asio::async_read(*m_socket, buffer, condition, std::move(token));
    }else{
        asio::async_read(*m_ssocket, buffer, condition, std::move(token));
    }
}

template<typename Buffer, typename Token>
void ITcpSocket::async_read_some(const Buffer& buffer, Token&& functor)
{
    if(!m_isSsl){
        m_socket->async_read_some(buffer, std::move(functor));
    }else{
        m_ssocket->async_read_some(buffer, std::move(functor));
    }
}

template<typename Buffer, typename Token>
void ITcpSocket::async_write(const Buffer& buffer, Token&& token)
{
    if(!m_isSsl){
        asio::async_write(*m_socket, buffer, std::move(token));
    }else{
        asio::async_write(*m_ssocket, buffer, std::move(token));
    }
}

$PackageWebCoreEnd
