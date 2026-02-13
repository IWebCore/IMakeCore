#pragma once

#include "core/util/IHeaderUtil.h"

$PackageWebCoreBegin

enum class IBeanTrait
{
    Tolerance = 1 << 0,
    Exact = 1 << 1,
    Full = 1 << 2
};

namespace detail
{
    std::map<std::string, QMetaMethod> getMethodMap(const QMetaObject&);
    IJson processToJson(const void*, const std::map<std::string, QMetaMethod>&);

    std::map<std::string, QMetaMethod> getRequiredMethodMap(const QMetaObject&);
    std::map<std::string, QMetaMethod> getOptionalMethodMap(const QMetaObject&);
    QMetaMethod getJsonValidatorMethod(const QMetaObject&);
    QVector<std::string> getFieldNames(const QMetaObject&);
    bool processLoadJson(const void* handle,
                         const IJson &value,
                         const IBeanTrait& beanTrait,
                         const std::map<std::string, QMetaMethod>& required,
                         const std::map<std::string, QMetaMethod>& optional,
                         const QVector<std::string>& fieldNames,
                         const QMetaMethod& validator);

    QMetaMethod getMetaMethod(const QMetaObject& meta, const QString &name);
    QStringList getRequiredFields(const QMetaObject& meta);
}

$PackageWebCoreEnd
