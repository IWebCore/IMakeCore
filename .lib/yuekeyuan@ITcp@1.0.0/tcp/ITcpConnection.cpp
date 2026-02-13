#include "ITcpConnection.h"
#include "tcp/ITcpSocket.h"
#include "core/application/asio/IAsioContext.h"
#include "tcp/ITcpResolver.h"
#include "tcp/ITcpManage.h"
#include <functional>

$PackageWebCoreBegin

ITcpConnection::ITcpConnection(ITcpSocket* socket, int resolverFactoryId)
    : m_socket(socket), m_resolverFactoryId(resolverFactoryId)
{
    startReadData();
}

ITcpConnection::~ITcpConnection()
{
    delete m_socket;
}

void ITcpConnection::doReadBy(std::size_t length)
{
    if(m_resolvers.empty()){
        return;
    }

    if(m_resolvers.back()->m_data.m_isConstBuffer){
        doReadDataBy(length);
    }else{
        doReadStreamBy(length);
    }
}

void ITcpConnection::doReadDataBy(std::size_t length)
{
    m_socket->async_read(m_resolvers.back()->m_data.getDataBuffer(), asio::transfer_exactly(length),
        [&](std::error_code error, std::size_t length){
            if(error){
                return doReadError(error);
            }
            m_resolvers.back()->m_data.m_readSize += length;
            m_resolvers.back()->resolve();
        }
    );
}

void ITcpConnection::doReadStreamBy(std::size_t length)
{
    m_socket->async_read(m_resolvers.back()->m_data.m_buffer, asio::transfer_exactly(length),
    [&](std::error_code error, std::size_t){
        if(error){
            return doReadError(error);
        }
        m_resolvers.back()->resolve();
    });
}

void ITcpConnection::doReadUtil(IStringView view, std::size_t startPos)
{
    if(m_resolvers.back()->m_data.m_isConstBuffer){
        doReadDataUtil(view, startPos);
    }else{
        doReadStreamUntil(view, startPos);
    }
}

void ITcpConnection::doReadDataUtil(IStringView view, std::size_t startPos)
{
    using namespace std::placeholders;
    auto functor = std::bind(std::mem_fn(&ITcpConnection::readDataUntilHandler), this, view, startPos, _1, _2);
    m_socket->async_read_some(m_resolvers.back()->m_data.getDataBuffer(), functor);
}

void ITcpConnection::doReadStreamUntil(IStringView view, std::size_t startPos)
{
    m_socket->async_read(m_resolvers.back()->m_data.m_buffer,
        [=](const std::error_code& error, std::size_t byteRead)-> std::size_t{
            Q_UNUSED(byteRead)
            if(error){
                return 0;
            }
            if(this->m_resolvers.back()->m_data.getBufferView().find(view, startPos) != std::string_view::npos){
                return 0;
            }
            return 1;
        },
        [&](std::error_code error, std::size_t byteRead){
            Q_UNUSED(byteRead)
            if(error){
                return doReadError(error);
            }
            this->m_resolvers.back()->resolve();
        }
    );
}

void ITcpConnection::doWrite(ITcpResolver* resolver)
{
    if(m_resolvers.front() != resolver){
        m_unWrittenCount ++;
        return;
    }

    doWriteImpl();
}

void ITcpConnection::doReadFinished()
{
    if(m_keepAlive){
        startReadData();
    }
}

void ITcpConnection::doWriteFinished()
{
    auto front = m_resolvers.front();
    ITcpManage::instance().destoryResolver(front);

    {
        std::lock_guard lock(m_mutex);
        m_resolvers.pop_front();
        m_deleteResolverCount++;
        if(m_unWrittenCount != 0){
            if(m_resolvers.front()->m_writeState == ITcpResolver::WriteState::Writing){
                m_unWrittenCount --;
                doWriteImpl();
            }
        }
    }

    if(!m_keepAlive && (m_addResolverCount == m_deleteResolverCount)){
        IAsioContext::post([=](){
            delete this;
        });
    }
}

void ITcpConnection::doReadError(std::error_code error)
{
    Q_UNUSED(error);

    m_keepAlive = false;
    auto back = m_resolvers.back();
    ITcpManage::instance().destoryResolver(back);

    {
        std::lock_guard lock(m_mutex);
        m_resolvers.pop_back();
        m_deleteResolverCount++;
    }

    if(m_addResolverCount == m_deleteResolverCount){
        IAsioContext::post([=](){
            delete this;
        });
    }
}

void ITcpConnection::doWriteError(std::error_code error)
{
    Q_UNUSED(error)
    auto front = m_resolvers.front();
    ITcpManage::instance().destoryResolver(front);

    {
        std::lock_guard lock(m_mutex);
        m_resolvers.pop_front();
        if(m_unWrittenCount != 0 && m_resolvers.front()->m_writeState == ITcpResolver::WriteState::Writing){
            m_unWrittenCount --;
            doWriteImpl();
        }
    }

    if(!m_keepAlive && (m_addResolverCount == m_deleteResolverCount)){
        IAsioContext::post([=](){
            delete this;
        });
    }
}

std::string ITcpConnection::remoteIp() const
{
    if(m_socket->m_isSsl){
        return m_socket->m_ssocket->lowest_layer().remote_endpoint().address().to_string();
    }
    return m_socket->m_socket->remote_endpoint().address().to_string();
}

void ITcpConnection::startReadData()
{
    auto resolver = ITcpManage::instance().createResolver(*this, m_resolverFactoryId);
    m_addResolverCount ++;
    {
        std::lock_guard lock(m_mutex);
        m_resolvers.push_back(resolver);
    }
    resolver->startRead();
}

void ITcpConnection::doWriteImpl()
{
    m_socket->async_write(m_resolvers.front()->getOutput(), [&](std::error_code err, std::size_t){
        if(err){
            return doWriteError(err);
        }
        m_resolvers.front()->m_writeCount --;
        m_resolvers.front()->m_writeState = ITcpResolver::WriteState::Finished;
        m_resolvers.front()->resolve();
    });
}

void ITcpConnection::readDataUntilHandler(IStringView view, std::size_t startPos, std::error_code error, std::size_t byteRead)
{
    if(error){
        return doReadError(error);
    }

    auto& data = m_resolvers.back()->m_data;
    data.m_readSize += byteRead;
    IStringView dataView(data.m_data, data.m_readSize);
    if(dataView.find(view, startPos) != std::string_view::npos){
        m_resolvers.back()->resolve();
    }else{
        using namespace std::placeholders;
        auto functor = std::bind(std::mem_fn(&ITcpConnection::readDataUntilHandler), this, view, startPos, _1, _2);
        m_socket->async_read_some(m_resolvers.back()->m_data.getDataBuffer(), functor);
    }
}

$PackageWebCoreEnd
