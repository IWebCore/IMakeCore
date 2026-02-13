#include "core/util/IHeaderUtil.h"

$IPackageBegin(packaging)

class Version
{
public:
    Version() = default;
    explicit Version(const std::vector<int>& segs);
    explicit Version(const char* version_str);
    explicit Version(const std::string& version_str);
    explicit Version(const QString& version_str);

public:
    bool isValid() const;
    int major() const;
    int minor() const;
    int patch() const;

public:
    bool operator<(const Version& other) const;
    bool operator<=(const Version& other) const;
    bool operator>(const Version& other) const;
    bool operator>=(const Version& other) const;
    bool operator==(const Version& other) const;
    bool operator!=(const Version& other) const;

private:
    static std::string trim(const std::string& str);

public:
    bool m_isVaild{false};
    std::vector<int> m_segments;
};

$IPackageEnd(packaging)
