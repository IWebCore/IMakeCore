#pragma once

#include "core/util/IHeaderUtil.h"

$PackageWebCoreBegin

class ICmdAction;
class ICmdRequest;
class ICmdArgs
{
private:
    using ParamType = std::array<void*, 11>;

public:
    ICmdArgs();

public:
    void execute(ICmdAction& action, const ICmdRequest& request);

private:
    bool validate(ICmdAction& action, const ICmdRequest& request);
    void invokePreMethod(ICmdAction& action, const ICmdRequest& request);
    void invokePostMethod(ICmdAction& action, const ICmdRequest& request);
    void invokeSetValueMethod(ICmdAction& action, const ICmdRequest& request);

public:
    bool m_nullable{false};
    QString m_name;
    QString m_memo;

    QMetaProperty m_prop{};
    QMetaMethod m_method{};
    QMetaMethod m_preMethod{};
    QMetaMethod m_postMethod{};
};

$PackageWebCoreEnd
