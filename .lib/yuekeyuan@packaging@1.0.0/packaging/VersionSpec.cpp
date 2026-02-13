#include "VersionSpec.h"
#include <iostream>
#include <sstream>

$IPackageBegin(packaging)

VersionSpec::VersionSpec(const std::string &spec_str) {
    std::istringstream iss(spec_str);
    std::string token;

    while (std::getline(iss, token, ',')) {
        token = trim(token);
        if (token.empty()) continue;

        // 解析操作符和版本
        Operator op;
        std::string version_str;
        bool has_wildcard = false;

        if (token.substr(0, 2) == "~=") {
            version_str = trim(token.substr(2));
            if (version_str.size() >= 2 && version_str.substr(version_str.size() - 2) == ".*") {
                return;
            }

            Version v(version_str);
            Version next_v = calculate_next_version(v);

            // 添加两个条件: >=v and < next_v
            m_specifiers.push_back({GREATER_THAN_EQUAL, v});
            m_specifiers.push_back({LESS_THAN, next_v});
            continue;
        }
        else if (token.substr(0, 2) == "==") {
            version_str = trim(token.substr(2));
            if (version_str.size() >= 2 && version_str.substr(version_str.size() - 2) == ".*") {
                has_wildcard = true;
                version_str = trim(version_str.substr(0, version_str.size() - 2));
            }

            if (has_wildcard) {
                Version v(version_str);
                Version next_v = calculate_next_version(v);

                m_specifiers.push_back({GREATER_THAN_EQUAL, v});
                m_specifiers.push_back({LESS_THAN, next_v});
            } else {
                op = EQUAL;
                Version v(version_str);
                m_specifiers.push_back({op, v});
            }
            continue;
        }
        else if (token.substr(0, 2) == "!=") {
            op = NOT_EQUAL;
            version_str = trim(token.substr(2));
        }
        else if (token.substr(0, 2) == "<=") {
            op = LESS_THAN_EQUAL;
            version_str = trim(token.substr(2));
        }
        else if (token.substr(0, 2) == ">=") {
            op = GREATER_THAN_EQUAL;
            version_str = trim(token.substr(2));
        }
        else if (token[0] == '<') {
            op = LESS_THAN;
            version_str = trim(token.substr(1));
        }
        else if (token[0] == '>') {
            op = GREATER_THAN;
            version_str = trim(token.substr(1));
        }
        else {
//            throw std::invalid_argument("Invalid operator: " + token);
            return;
        }

        // 检查通配符（只允许在 == 中使用）
        if (version_str.size() >= 2 && version_str.substr(version_str.size() - 2) == ".*") {
//            throw std::invalid_argument("Wildcard only allowed with ==");
            return;
        }

        Version v(version_str);
        m_specifiers.push_back({op, v});
    }
    m_isValid = true;
}

bool VersionSpec::isValid() const
{
    return m_isValid;
}

bool VersionSpec::contain(const std::string &version_str) const {
    Version v(version_str);
    return contain(v);
}

bool VersionSpec::contain(const Version &v) const
{
    for (const auto& spec : m_specifiers) {
        switch (spec.op) {
        case EQUAL:
            if (!(v == spec.version)) return false;
            break;
        case NOT_EQUAL:
            if (v == spec.version) return false;
            break;
        case LESS_THAN:
            if (!(v < spec.version)) return false;
            break;
        case LESS_THAN_EQUAL:
            if (!(v <= spec.version)) return false;
            break;
        case GREATER_THAN:
            if (!(v > spec.version)) return false;
            break;
        case GREATER_THAN_EQUAL:
            if (!(v >= spec.version)) return false;
            break;
        }
    }
    return true;
}

std::string VersionSpec::trim(const std::string &str) {
    size_t start = str.find_first_not_of(" ");
    size_t end = str.find_last_not_of(" ");
    if (start == std::string::npos) return "";
    return str.substr(start, end - start + 1);
}

Version VersionSpec::calculate_next_version(const Version &v) {
    if (v.m_segments.empty()) {
        return Version(std::vector<int>{0});
    }

    std::vector<int> next_segments;
    size_t k = v.m_segments.size();

    if (k == 1) {
        next_segments = {v.m_segments[0] + 1};
    } else {
        // 取前 k-1 段，最后一段加1
        next_segments = std::vector<int>(v.m_segments.begin(), v.m_segments.end() - 1);
        next_segments.back() += 1;
    }

    return Version(next_segments);
}

$IPackageEnd(packaging)
