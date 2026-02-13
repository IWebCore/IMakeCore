#pragma once

#include "core/util/IHeaderUtil.h"
#include "core/unit/INoCopyMoveUnit.h"
#include "rdb/IRdbManage.h"
#include "rdb/entity/IRdbEntityInfo.h"

$PackageWebCoreBegin

class IRdbTableInfo : public IRdbEntityInfo, public INoCopyMoveUnit
{
public:
    enum ValueMakerType{
        ReadValue,
        InsertValue,
        GenerateValue,
    };
    struct ValueMaker{
        int index{};
        ValueMakerType type{ValueMakerType::ReadValue};
        QString insertValue;
        IRdbManage::GeneratorFunction generator;
    };

public:
    IRdbTableInfo() = delete;
    explicit IRdbTableInfo(const QMetaObject& meta);

public:
    int m_primaryKey {-1};
    int m_autoIncrement{-1};
    QList<int> m_notNullKeys;   // note: this int value relate to fields, not meta4
    QList<int> m_uniqueKeys;
    QStringList m_ignoredKeys;
    QMap<int, QString> m_constraints;
    QMap<int, QString> m_sqlType;
    QVector<ValueMaker> m_valueMakers;
};

$PackageWebCoreEnd
