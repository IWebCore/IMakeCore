#include "ITcpSocket.h"
#include <iostream>

$PackageWebCoreBegin

ITcpSocket::ITcpSocket(ITcpSocket::ISocket && socket)
    :m_isSsl(false), m_ssocket(nullptr), m_socket(new ISocket(std::move(socket)))
{
}

ITcpSocket::ITcpSocket(ITcpSocket::ISSocket* socket)
    : m_isSsl(true), m_ssocket(socket), m_socket(nullptr)
{
}

ITcpSocket::~ITcpSocket()
{
    if(is_open()){
        close();
    }

    if(!m_isSsl){
        delete m_socket;
    }else{
        delete m_ssocket;
    }
}

bool ITcpSocket::is_open() const
{
#ifdef IWEBCORE_ENABLE_SSL
    if(m_isSsl){
        return m_ssocket->lowest_layer().is_open();
    }
#endif
    return m_socket->is_open();
}

void ITcpSocket::close()
{
#ifdef IWEBCORE_ENABLE_SSL
    if(m_isSsl){
        try{
            m_ssocket->shutdown();
            m_ssocket->lowest_layer().shutdown(ISocket::shutdown_both);
            m_ssocket->lowest_layer().close();
        } catch (const std::exception& e) {
            std::cout << e.what() << std::endl;
            qDebug() << "Error during connection shutdown: " << e.what();
        }
        return;
    }
#endif
    return m_socket->close();
}

$PackageWebCoreEnd
