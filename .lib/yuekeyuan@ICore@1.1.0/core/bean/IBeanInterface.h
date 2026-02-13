#pragma once

#ifdef IWEBCORE_FLATTEN_CRTP

#include "IBeanInterface_flatten.h"

#else

#include "IBeanAbort.h"
#include "IBeanTypeManage.h"
#include "IBeanPreProcessor.h"
#include "core/base/IResult.h"
#include "core/util/IMetaUtil.h"
#include "core/unit/ITraceUnit.h"
#include "core/bean/detail/IBeanInterfaceDetail.h"
#include "core/unit/IRegisterMetaTypeUnit.h"
#include "core/task/unit/ITaskInstantUnit.h"

$PackageWebCoreBegin

template<typename T, bool enabled = true, IBeanTrait trait = IBeanTrait::Tolerance>
class IBeanInterface : public ITaskInstantUnit<T, enabled>
{
public:
    virtual void $task() override;

public:
    virtual IJson toJson() const;
    virtual bool loadJson(const IJson &value, const IBeanTrait& = trait);
    static IResult<T> fromJson(const IJson& value, const IBeanTrait& = trait);
};


template<typename T, bool enabled, IBeanTrait trait>
IJson IBeanInterface<T, enabled, trait>::toJson() const
{
    static const auto methodMap = detail::getMethodMap(T::staticMetaObject);
    return detail::processToJson(this, methodMap);
}

template<typename T, bool enabled, IBeanTrait trait>
bool IBeanInterface<T, enabled, trait>::loadJson(const IJson &value, const IBeanTrait& beanTrait)
{
    static const auto required = detail::getRequiredMethodMap(T::staticMetaObject);
    static const auto optional = detail::getOptionalMethodMap(T::staticMetaObject);
    static const auto fieldNames = detail::getFieldNames(T::staticMetaObject);
    static const auto validator = detail::getJsonValidatorMethod(T::staticMetaObject);
    return detail::processLoadJson(this, value, beanTrait, required, optional, fieldNames, validator);
}

template<typename T, bool enabled, IBeanTrait trait>
IResult<T> IBeanInterface<T, enabled, trait>::fromJson(const IJson& value, const IBeanTrait& beanTrait)
{
    T t;
    if(t.loadJson(value, beanTrait)){
        return t;
    }
    return std::nullopt;
}

template<typename T, bool enabled, IBeanTrait trait>
void IBeanInterface<T, enabled, trait>::$task()
{
    IRegisterMetaTypeUnit<T>::registType();
    IRegisterMetaTypeUnit<T>::registerBean();
}

$PackageWebCoreEnd

#endif
