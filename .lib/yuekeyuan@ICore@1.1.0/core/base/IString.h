#pragma once

#include <QMetaType>
#include <string>
#include <list>
#include <vector>
#include "core/base/IStringView.h"
#include "core/base/IResult.h"

#ifndef __I_STRING_GUARD__
#define __I_STRING_GUARD__

class IString
{
private:
    enum class Type {
        IStringView, // default, and empty
        QByteArray,
        StdString,
    };

public:
    IString() = default;
    ~IString();

    template<std::size_t N>
    IString(const char(*)[N]);
    IString(const char**);
    IString(const IString*);
    IString(const std::string*);
    IString(const QByteArray*);
    IString(const IStringView*);

    IString(const char*);
    IString(IStringView stringView);
    IString(const QString&) noexcept;

    IString(const IString& other);
    IString(IString&& other) noexcept;

    IString(const QByteArray& byteArray);
    IString(QByteArray&& byteArray) noexcept;

    IString(const std::string& stdString);
    IString(std::string&& stdString) noexcept;

    template<std::size_t N>
    IString& operator=(const char(*)[N]);
    IString& operator=(const char**);
    IString& operator=(const IString*);
    IString& operator=(const QByteArray*);
    IString& operator=(const std::string*);
    IString& operator=(const IStringView*);

    IString& operator=(const char*);
    IString& operator=(IStringView stringView);
    IString& operator=(const QString&);

    IString& operator=(const IString& other);
    IString& operator=(IString&& other) noexcept;

    IString& operator=(const QByteArray& byteArray);
    IString& operator=(QByteArray&& byteArray) noexcept;
    IString& operator=(const std::string& stdString);
    IString& operator=(std::string&& stdString) noexcept;
    IString& operator=(std::nullptr_t);

    bool operator == (const char*) const;
    bool operator == (IStringView) const;
    bool operator == (const IString&) const;
    bool operator == (const std::string&) const;
    bool operator == (const QByteArray&) const;
    bool operator != (const char*) const;
    bool operator != (IStringView) const;
    bool operator != (const IString&) const;
    bool operator != (const std::string&) const;
    bool operator != (const QByteArray&) const;

    bool operator <(const IString&) const;

public:
    std::size_t length() const;
    std::size_t size() const;
    bool isSolid() const;
    bool isEmpty() const;
    IString& solidify();
    operator bool() const;
    operator IStringView() const;

public:
    template<typename T>
    IResult<T> value() const;

public:
    IStringViewList split(char) const;
    IStringViewList split(const IString&) const;
    bool startWith(const IString&) const;
    bool equal(const IString&) const;
    bool equalIgnoreCase(const IString&) const;
    bool containIgnoreCase(const IString&) const;

public:
    QString toQString() const;
    std::string toStdString() const;
    QByteArray toQByteArray() const;

private:
    void clear();
    void copyFrom(const IString& other);
    void moveFrom(IString&& other) noexcept;

private:
    Type m_type{Type::IStringView};
    void* m_data{nullptr};

public:
    IStringView m_view{};
};

template<std::size_t N>
IString::IString(const char (*data)[N] )
    : m_view(*data, N-1)
{
}

template<std::size_t N>
IString& IString::operator=(const char (*data)[N])
{
    clear();
    m_view = IStringView(*data, N-1);
    return *this;
}

extern template class QList<IString>;
#if QT_VERSION < QT_VERSION_CHECK(6, 0, 0)
    extern template class QVector<IString>;
#endif

extern template class std::list<IString>;
extern template class std::vector<IString>;

using IStringList = QList<IString>;

Q_DECLARE_METATYPE(IString)

#endif
