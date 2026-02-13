#pragma once

#include "core/util/IHeaderUtil.h"
#include "cmd/memo/ICmdActionArgsMemo.h"
#include "cmd/memo/ICmdActionOptionMemo.h"
#include "cmd/action/ICmdAction.h"

$PackageWebCoreBegin

class ICmdActionMemo
{
public:
    ICmdActionMemo(const ICmdAction*);

private:
    ICmdActionOptionMemo createOptionMemo(const ICmdOptionValue* opt, const ICmdAction* act);

public:
    QString m_memo;
    QStringList m_path;
    QList<ICmdActionOptionMemo> m_optionMemo;
};

$PackageWebCoreEnd
