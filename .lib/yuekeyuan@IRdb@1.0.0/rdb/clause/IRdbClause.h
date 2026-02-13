#pragma once

#include "core/util/IHeaderUtil.h"

$PackageWebCoreBegin

class ISqlQuery;
class IRdbClause
{
public:
    IRdbClause() = default;

public:
    mutable QMap<QString, QVariant> m_boundValue;
};

namespace IRdb
{
    enum Relation
    {
        And = 0b10,
        AndNot = 0b00,
        Or =  0b11,
        OrNot = 0b01,
    };
}

$PackageWebCoreEnd
