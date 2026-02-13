#include "IStringView.h"
#include "core/base/IString.h"

namespace std {
    template <>
    struct hash<IStringView> {
        size_t operator()(const IStringView& obj) const {
            return IStringView::qHash(obj);
        }
    };
}

IStringView::IStringView(const std::string &data)
    : std::string_view(data)
{
}

IStringView::IStringView(const QByteArray &data)
    : std::string_view(data.data(), data.length())
{
}

IStringView::IStringView(const char **data)
    : std::string_view(*data)
{
}

IStringView::IStringView(const IString *data)
    : std::string_view(data->m_view)
{
}

IStringView::IStringView(const std::string *data)
    : std::string_view(*data)
{

}

IStringView::IStringView(const QByteArray *data)
    : IStringView(*data)
{
}

bool IStringView::operator ==(const char * data) const
{
    return operator ==(IStringView(data));
}

bool IStringView::operator ==(IStringView data) const
{
    if(this->length() != data.length()){
        return false;
    }
    if(this->length() == 0 || this->data() == data.data()){    // empty equals empty
        return true;
    }
    return memcmp(this->data(), data.data(), this->length() * sizeof(IStringView::value_type)) == 0;
}

bool IStringView::operator !=(const char* data) const
{
    return ! this->operator ==(data);
}

bool IStringView::operator !=(IStringView data) const
{
    return !this->operator ==(data);
}

bool IStringView::operator <(const char* data) const
{
    return this->operator <(IStringView(data));
}

bool IStringView::operator <(IStringView data) const
{
    return std::string_view(*this) < std::string_view(data);
}

uint IStringView::qHash(IStringView key, uint seed)
{
    size_t hash = seed;
    const size_t length = key.size();
    const char* data = key.data();

    for (size_t i = 0; i < length; ++i) {
        hash = (hash * 131) + static_cast<size_t>(data[i]);
    }
    return static_cast<uint>(hash);
}

QString IStringView::toQString() const
{
    return QString::fromStdString(std::string(*this));
}

std::string IStringView::toStdString() const
{
    return std::string(*this);
}

QByteArray IStringView::toQByteArray() const
{
    return QByteArray(data(), static_cast<int>(length()));
}

IStringView IStringView::substr(const size_type _Off, size_type _Count) const
{
    return IStringView(std::string_view::substr(_Off, _Count));
}

IStringView IStringView::trimmed()
{
    auto left = find_first_not_of(" \r\n\t");
    if (left == std::string_view::npos) {
        return "";
    }
    auto right = find_last_not_of(" \r\n\t");
    return substr(left, right - left + 1);
}

IStringViewList IStringView::split(char delimiter) const
{
    IStringViewList tokens;
    std::string_view::size_type start = 0;
    std::string_view::size_type end = this->find(delimiter);

    while (end != std::string_view::npos) {
        tokens.append(IStringView(this->substr(start, end - start)));
        start = end + 1;
        end = this->find(delimiter, start);
    }

    tokens.append(IStringView(this->substr(start, end)));
    return tokens;
}

// NOTE: 性能改进
IStringViewList IStringView::split(IStringView delimiter) const
{
    IStringViewList result;
    result.reserve(static_cast<int>(this->size() / 4));

    size_t start = 0;
    size_t end = find(delimiter);
    while (end != std::string_view::npos) {
        result.push_back(substr(start, end - start));
        start = end + delimiter.length();
        end = find(delimiter, start);
    }

    result.append(substr(start));
    return result;
}

bool IStringView::startWith(IStringView prefix) const
{
    if(prefix.size() == 0 || prefix.size() > this->size()){
        return false;
    }
    return this->substr(0, prefix.length()) == prefix;
}

bool IStringView::endWith(IStringView suffix) const
{
    if(this->size() < suffix.size()){
        return false;
    }
    return this->substr(this->size() - suffix.size()) == suffix;
}

bool IStringView::equalIgnoreCase(IStringView piece) const
{
    if (piece.length() != length()) {
        return false;
    }
    return std::equal(this->begin(), this->end(), piece.begin(),
        [](char a, char b) {
            return std::tolower(static_cast<unsigned char>(a)) == std::tolower(static_cast<unsigned char>(b));
        }
    );
}

bool IStringView::containIgnoreCase(IStringView data) const
{
    if (data.size() > size()) {
        return false;
    }

    auto it = std::search(this->begin(), this->end(), data.begin(), data.end(),
        [](char a, char b) {
            return std::tolower(static_cast<unsigned char>(a)) == std::tolower(static_cast<unsigned char>(b));
        });

    return it != this->end();
}

IStringViewList::IStringViewList(QList<IStringView> data)
    : QList<IStringView>(std::move(data))
{
}

std::string IStringViewList::join(IStringView spliter)
{
    if (isEmpty()) {
        return "";
    }

    size_t total_length = 0;
    for (const auto& piece : *this) {
        total_length += piece.size();
    }
    total_length += spliter.size() * (size() - 1); // 加上分隔符的长度

    std::string result;
    result.reserve(total_length);
    for (int i = 0; i < size(); ++i) {
        result += this->at(i);
        if (i < size() - 1) {
            result += spliter;
        }
    }
    return result;
}
