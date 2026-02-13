#pragma once

#include "core/util/IHeaderUtil.h"

$PackageWebCoreBegin

class INodyException : std::exception
{
public:
    INodyException(const IString& error, const IString& content);
    virtual const char *what() const noexcept final;

private:
    std::string m_error;
};

$PackageWebCoreEnd
