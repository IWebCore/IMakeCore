#pragma once

#include "core/util/IHeaderUtil.h"
#include "core/config/IConfigManageInterface.h"
#include "core/unit/ISoloUnit.h"

$PackageWebCoreBegin

class IProfileManage final : public IConfigManageInterface, public ISoloUnit<IProfileManage>
{
public:
    IProfileManage() = default;
};

$PackageWebCoreEnd
