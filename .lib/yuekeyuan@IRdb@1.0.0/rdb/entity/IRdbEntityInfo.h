#pragma once

#include "core/util/IHeaderUtil.h"

$PackageWebCoreBegin

class IRdbEntityInfo
{
public:
    struct Field
    {
        QString m_name;
        QString m_typeName;
        QMetaType::Type m_typeId;
        QMetaProperty m_property;
    };

public:
    explicit IRdbEntityInfo(const QMetaObject& meta);

public:
    const QMetaObject& m_metaObject;

public:
    QString m_className;
    QString m_entityName;

    QList<Field> m_fields;
    QStringList m_fieldNames;
};

$PackageWebCoreEnd
