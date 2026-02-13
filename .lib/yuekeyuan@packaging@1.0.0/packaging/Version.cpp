#include "Version.h"
#include <sstream>

$IPackageBegin(packaging)

Version::Version(const std::vector<int> &segs)
{
    m_segments = segs;
    while (m_segments.size() < 3) {
        m_segments.push_back(0);
    }
    m_isVaild = true;
}

Version::Version(const char *version_str)
    : Version(std::string(version_str))
{
}

Version::Version(const std::string &version_str) {
    std::string str = trim(version_str);
    std::istringstream iss(str);
    std::string token;

    while (std::getline(iss, token, '.')) {
        token = trim(token);
        if (token.empty()) continue;

        // 尝试转换为整数
        try {
            int num = std::stoi(token);
            m_segments.push_back(num);
        } catch (...) {
            // 遇到非数字部分，停止解析
            return;
        }
    }

    while (m_segments.size() < 3) {
        m_segments.push_back(0);
    }
    m_isVaild = true;
}

Version::Version(const QString &version_str)
    : Version(version_str.toStdString())
{
}

bool Version::isValid() const
{
    return m_isVaild;
}

int Version::major() const
{
    return m_segments[0];
}

int Version::minor() const
{
    return m_segments[1];
}

int Version::patch() const
{
    return m_segments[2];
}

bool Version::operator<(const Version &other) const {
    for (size_t i = 0; i < 3; ++i) {
        if(this->m_segments[i] == other.m_segments[i]){
            continue;
        }
        return this->m_segments[i] < other.m_segments[i];
    }
    return false;
}

bool Version::operator<=(const Version &other) const {
    return (*this < other) || (*this == other);
}

bool Version::operator>(const Version &other) const {
    return other < *this;
}

bool Version::operator>=(const Version &other) const {
    return (*this > other) || (*this == other);
}

bool Version::operator==(const Version &other) const {
    for(int i=0; i<3; i++){
        if(this->m_segments[i] != other.m_segments[i]){
            return false;
        }
    }
    return true;
}

bool Version::operator!=(const Version &other) const {
    return !(*this == other);
}

std::string Version::trim(const std::string &str) {
    size_t start = str.find_first_not_of(" ");
    size_t end = str.find_last_not_of(" ");
    if (start == std::string::npos) return "";
    return str.substr(start, end - start + 1);
}

$IPackageEnd(packaging)
