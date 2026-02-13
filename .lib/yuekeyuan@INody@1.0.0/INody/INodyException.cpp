#include "INodyException.h"

$PackageWebCoreBegin

namespace detail
{
    std::string makeTrace(const IString &error, const IString &content)
    {
        auto len = content.length();
        QString brief;
        if(len < 100){
            brief = content.toQString().left(100);
        }else {
            brief = content.toQString().left(50).append(" ...... ").append(content.toQString().right(50));
        }
        QString ret = QString("ERROR: ").append(error.toQString()).append("\n\tNEAR: ").append(brief);
        return ret.toStdString();
    }
}


INodyException::INodyException(const IString &error, const IString& content)
{
    m_error = detail::makeTrace(error, content);
}

const char *INodyException::what() const noexcept
{
    return m_error.c_str();
}


$PackageWebCoreEnd
