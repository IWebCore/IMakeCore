#pragma once

#include <string_view>
#include <QString>
#include <QByteArray>
#include <QList>
#include "core/base/IResult.h"

#ifndef __I_STRING_VIEW_GUARD__
#define __I_STRING_VIEW_GUARD__

class IString;
class IStringView;
class IStringViewList;
class IStringView : public std::string_view
{
public:
    IStringView() = default;
    IStringView(const std::string& data);
    IStringView(const QByteArray& data);

    template<std::size_t N>
    IStringView(const char(*)[N]);

    IStringView(const char**);
    IStringView(const IString* data);
    IStringView(const std::string* data);
    IStringView(const QByteArray* data);

    constexpr IStringView(std::string_view data);
    constexpr IStringView(const char* data, std::size_t length);
    constexpr IStringView(const char* data);
    constexpr IStringView(const IStringView& data);

public:
    constexpr IStringView& operator=(const IStringView&) noexcept = default;
    constexpr IStringView& operator=(IStringView&&) noexcept = default;

    bool operator == (const char*) const;
    bool operator == (IStringView) const;
    bool operator !=(const char*) const;
    bool operator !=(IStringView) const;
    bool operator <(const char*) const;
    bool operator <(IStringView) const;

public:
    static uint qHash(IStringView obj, uint seed = 0);

public:
    QString toQString() const;
    std::string toStdString() const;
    QByteArray toQByteArray() const;

public:
    IStringView substr(const size_type _Off, size_type _Count=std::string::npos) const;
    IStringView trimmed();
    IStringViewList split(char) const;
    IStringViewList split(IStringView) const;
    bool startWith(IStringView prefix) const;
    bool endWith(IStringView suffix) const;
    bool equalIgnoreCase(IStringView) const;
    bool containIgnoreCase(IStringView) const;
};

template<std::size_t N>
IStringView::IStringView(const char(*data)[N])
    : std::string_view(*data, N-1)
{
}

inline constexpr IStringView::IStringView(std::string_view data)
    : std::string_view(data)
{
}

inline constexpr IStringView::IStringView(const char *data)
    : std::string_view(data)
{
}

inline constexpr IStringView::IStringView(const char *data, std::size_t length)
    : std::string_view(data, length)
{
}

inline constexpr IStringView::IStringView(const IStringView& view)
    : std::string_view(static_cast<std::string_view>(view))
{
}

inline uint qHash(IStringView key, uint seed = 0) noexcept
{
    return IStringView::qHash(key, seed);
}

class IStringViewList : public QList<IStringView>
{
public:
    IStringViewList() = default;
    IStringViewList(QList<IStringView> data);

public:
    std::string join(IStringView);
};


#endif
