#pragma once

#include "core/util/IHeaderUtil.h"

class ICmdActionOptionMemo
{
public:
    ICmdActionOptionMemo();

public:
    // TODO: 添加是否没有参数的限制
    bool m_isRequired{false};
    QString m_name;
    QString m_shortName;
    QString m_memo;
};
