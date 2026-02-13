#include "INodyResponse.h"
#include "INody/INodyManage.h"
#include "http/invalid/IHttpNotFoundInvalid.h"
#include "http/invalid/IHttpBadRequestInvalid.h"
#include "http/invalid/IHttpInternalErrorInvalid.h"

$PackageWebCoreBegin

INodyResponse::INodyResponse(const QString &path, const IJson &json)
    : INodyResponse(path.toStdString(), json)
{
}

INodyResponse::INodyResponse(const char *path, const IJson &json)
{
    if(INodyManage::instance().canParse(IString(path))){
        auto data = INodyManage::instance().parse(IString(path), json);
        m_raw->setMime(IHttpMime::TEXT_HTML_UTF8);
        m_raw->setContent(new IHttpResponseContent(IString(data)));
        return;
    }
    m_raw->setContent(ISolo<IHttpInternalErrorInvalid>());
}

INodyResponse::INodyResponse(const std::string &path, const IJson &json)
{
    if(INodyManage::instance().canParse(IString(&path))){
        auto data = INodyManage::instance().parse(IString(&path), json);
        m_raw->setMime(IHttpMime::TEXT_HTML_UTF8);
        m_raw->setContent(new IHttpResponseContent(IString(data)));
        return;
    }
    m_raw->setContent(ISolo<IHttpInternalErrorInvalid>());
}

INodyResponse::INodyResponse(const IString &path, const IJson &json)
{
    if(INodyManage::instance().canParse(path)){
        auto data = INodyManage::instance().parse(path, json);
        m_raw->setMime(IHttpMime::TEXT_HTML_UTF8);
        m_raw->setContent(new IHttpResponseContent(IString(data)));
        return;
    }
    m_raw->setContent(ISolo<IHttpInternalErrorInvalid>());
}

void INodyResponse::setContent(const IHttpInvalidWare &ware)
{
    return IHttpResponseInterface::setContent(ware);
}

$PackageWebCoreEnd
