#pragma once

#include "core/util/IHeaderUtil.h"

$PackageWebCoreBegin

class ICmdAction;
class ICmdRequest;
class ICmdArgx
{
private:
    using ParamType = std::array<void*, 11>;

public:
    ICmdArgx();

public:
    void execute(ICmdAction& action, const ICmdRequest& request);

private:
    bool validate(ICmdAction& action, const ICmdRequest& request);
    void invokePreMethod(ICmdAction& action, const ICmdRequest& request);
    void invokePostMethod(ICmdAction& action, const ICmdRequest& request);
    void invokeSetValueMethod(ICmdAction& action, const ICmdRequest& request);

public:
    int m_index{};
    bool m_nullable{false};
    QString m_name;
    QString m_memo;

    QMetaProperty m_property{};
    QMetaMethod m_method{};
    QMetaMethod m_preMethod{};
    QMetaMethod m_postMethod{};
};

$PackageWebCoreEnd
