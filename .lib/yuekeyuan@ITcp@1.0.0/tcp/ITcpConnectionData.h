#pragma once

#include "core/util/IHeaderUtil.h"
#include "asio.hpp"

$PackageWebCoreBegin

struct ITcpConnectionData
{
public:
    ITcpConnectionData();
    ~ITcpConnectionData();

public:
    auto getDataBuffer(){
        return asio::buffer(m_data + m_readSize, m_maxSize - m_readSize);
    }

    IStringView getBufferView(std::size_t length = std::string_view::npos);
    IStringView getUnResolvedDataView();

    IStringView readBy(std::size_t length);
    IStringView readLine();
    IStringView readPartition();
    std::size_t find(IStringView view);
    std::size_t getUnparsedLength() const;

public:
    char* m_data;
    bool m_isConstBuffer{true};

public:
    static constexpr auto m_maxSize = 1024*10;  // TODO:
    std::size_t m_readSize{};
    std::size_t m_parsedSize{};

public:
    asio::streambuf m_buffer;
};

$PackageWebCoreEnd
