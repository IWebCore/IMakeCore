#pragma once

#include "core/util/IHeaderUtil.h"
#include "core/config/IConfigManageInterface.h"
#include "core/unit/ISoloUnit.h"

$PackageWebCoreBegin

class IContextManage final : public IConfigManageInterface, public ISoloUnit<IContextManage>
{
public:
    IContextManage() = default;
};

$PackageWebCoreEnd
