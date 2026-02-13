#pragma once

#include "core/util/IHeaderUtil.h"
#include "http/response/IHttpResponseInterface.h"

$PackageWebCoreBegin

class INodyResponse : public IHttpResponseInterface<INodyResponse>
{
    $AsResponseNoPrefix(INodyResponse)
public:
    using IHttpResponseInterface::IHttpResponseInterface;
    using IHttpResponseInterface::operator [];

private:
    using IHttpResponseInterface::setContent;

public:
    INodyResponse(const QString& path, const IJson& data);
    INodyResponse(const char* path, const IJson& data);
    INodyResponse(const std::string&, const IJson& data);
    INodyResponse(const IString&, const IJson& data);

public:
    void setContent(const IHttpInvalidWare& ware);
};

$PackageWebCoreEnd
