#pragma once

#ifdef IWEBCORE_FLATTEN_CRTP

#include "IRdbViewInterface_flatten.h"

#else

#include "core/util/IHeaderUtil.h"
#include "core/bean/IBeanInterface.h"
#include "rdb/entity/IRdbViewInfo.h"
#include "rdb/pp/IRdbViewPreProcessor.h"

$PackageWebCoreBegin

template<typename T, bool enabled = true, IBeanTrait trait = IBeanTrait::Tolerance>
class IRdbViewInterface : public IBeanInterface<T, enabled, trait>
{
public:
    IRdbViewInterface() = default;

public:
    static const IRdbViewInfo& staticEntityInfo();
};

template<typename T, bool enabled, IBeanTrait trait>
const IRdbViewInfo &IRdbViewInterface<T, enabled, trait>::staticEntityInfo()
{
    static IRdbViewInfo s_info(T::staticMetaObject);
    return s_info;
}

$PackageWebCoreEnd

#endif
