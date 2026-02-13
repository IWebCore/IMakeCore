#pragma once

#include "core/util/IHeaderUtil.h"

$PackageWebCoreBegin

class ICmdAction;
class ICmdRequest;
class ICmdOption
{
private:
    using ParamType = std::array<void*, 11>;

public:
    ICmdOption() = default;

public:
    void execute(ICmdAction& action, const ICmdRequest& request);

private:
    bool validate(ICmdAction& action, const ICmdRequest& request);
    void invokePreMethod(ICmdAction& action, const ICmdRequest& request);
    void invokePostMethod(ICmdAction& action, const ICmdRequest& request);
    void invokeSetValueMethod(ICmdAction& action, const ICmdRequest& request);

private:
    bool existOption(const ICmdRequest& request) const;

public:
    bool m_isRequired{false};
    bool m_isNoValue{false};
    QString m_name;
    QString m_shortName;
    QString m_memo;

    QMetaProperty m_property;
    QMetaMethod m_method;           // 设置 method
    QMetaMethod m_preMethod;
    QMetaMethod m_postMethod;
};

$PackageWebCoreEnd
