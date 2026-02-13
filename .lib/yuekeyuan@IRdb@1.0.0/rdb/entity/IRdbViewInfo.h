#pragma once

#include "core/util/IHeaderUtil.h"
#include "rdb/entity/IRdbEntityInfo.h"

$PackageWebCoreBegin

class IRdbViewInfo : public IRdbEntityInfo
{
public:
    IRdbViewInfo() = delete;
    explicit IRdbViewInfo(const QMetaObject& meta);

public:
    QString m_createViewSql;
};

$PackageWebCoreEnd
