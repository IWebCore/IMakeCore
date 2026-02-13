#include "IStringViewStash.h"

$PackageWebCoreBegin

IStringView IStringViewStash::stash(const char *data) const
{
    return stash(QByteArray(data));
}

IStringView IStringViewStash::stash(QByteArray &&data) const
{
    m_stashed.emplace_back(std::move(data));
    return m_stashed.back();
}

IStringView IStringViewStash::stash(const QByteArray &data) const
{
    m_stashed.emplace_back(data);
    return m_stashed.back();
}

IStringView IStringViewStash::stash(const QString &data) const
{
    m_stashed.emplace_back(data.toUtf8());
    return m_stashed.back();
}

IStringView IStringViewStash::stash(std::string &&data) const
{
    m_stashed.emplace_back(std::move(data));
    return m_stashed.back();
}

IStringView IStringViewStash::stash(const std::string &data) const
{
    m_stashed.emplace_back(std::move(data));
    return m_stashed.back();
}

IStringView IStringViewStash::stash(IString &&data) const
{
    m_stashed.emplace_back(std::move(data.solidify()));
    return m_stashed.back();
}

IStringView IStringViewStash::stash(const IString &data) const
{
    IString value = data;
    m_stashed.emplace_back(std::move(value.solidify()));
    return m_stashed.back();
}

IStringView IStringViewStash::stash(IStringView data) const
{
    IString value = data;
    m_stashed.emplace_back(std::move(value.solidify()));
    return m_stashed.back();
}

$PackageWebCoreEnd
