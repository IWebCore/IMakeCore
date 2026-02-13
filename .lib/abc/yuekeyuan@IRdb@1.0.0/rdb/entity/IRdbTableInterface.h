#pragma once

#ifdef IWEBCORE_FLATTEN_CRTP

#include "IRdbTableInterface_flatten.h"

#else

#include "core/util/IHeaderUtil.h"
#include "core/bean/IBeanInterface.h"
#include "rdb/entity/IRdbTableInfo.h"
#include "rdb/pp/IRdbTablePreProcessor.h"

$PackageWebCoreBegin

template<typename T, bool enabled=true, IBeanTrait trait = IBeanTrait::Tolerance>
class IRdbTableInterface : public IBeanInterface<T, enabled, trait>
{
public:
    IRdbTableInterface() = default;

public:
    static const IRdbTableInfo& staticEntityInfo();
};

template<typename T, bool enabled, IBeanTrait trait>
const IRdbTableInfo& IRdbTableInterface<T, enabled, trait>::staticEntityInfo()
{
    static IRdbTableInfo s_info(T::staticMetaObject);
    return s_info;
}

$PackageWebCoreEnd

#endif
