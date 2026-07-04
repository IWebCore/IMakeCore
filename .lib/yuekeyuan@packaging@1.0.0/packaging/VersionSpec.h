#include "Version.h"

$IPackageBegin(packaging)

class VersionSpec
{
public:
    enum Operator {
        EQUAL,           // ==
        NOT_EQUAL,       // !=
        LESS_THAN,       // <
        LESS_THAN_EQUAL, // <=
        GREATER_THAN,    // >
        GREATER_THAN_EQUAL, // >=
        // COMPATIBLE (~=) 在解析时转换为 >= 和 <
    };

    struct Specifier {
        Operator op;
        Version version;
    };

public:
    explicit VersionSpec(const std::string& spec_str);

public:
    bool isValid() const;
    bool contain(const std::string& version_str) const;
    bool contain(const Version& version) const;


private:
    static std::string trim(const std::string& str);
    static Version calculate_next_version(const Version& v);

private:
    bool m_isValid{false};
    std::vector<Specifier> m_specifiers;
};

$IPackageEnd(packaging)
