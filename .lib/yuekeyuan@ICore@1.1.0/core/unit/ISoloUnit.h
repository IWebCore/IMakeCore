#pragma once

#include "core/util/IMetaUtil.h"
#include "core/util/ITraitUtil.h"

$PackageWebCoreBegin

template<typename T>
class ISoloUnit
{
protected:
    ISoloUnit();
    virtual ~ISoloUnit() = default;

    ISoloUnit(ISoloUnit&&) = delete;
    ISoloUnit(const ISoloUnit&) = delete;
    ISoloUnit& operator=(ISoloUnit&&) = delete;
    ISoloUnit& operator=(const ISoloUnit&) = delete;

public:
    static T& instance();
};

namespace ISoloUnitDetail
{
    void abortError(QString);
}

template<typename T>
T& ISoloUnit<T>::instance()
{
    static T instance{};
    return instance;
}

template<typename T>
ISoloUnit<T>::ISoloUnit()
{
    static std::atomic_bool flag{false};
    if(flag){
        ISoloUnitDetail::abortError("class name:" + IMetaUtil::getTypeName<T>());
    }
    flag = true;
}

template<typename T>
std::enable_if_t<has_class_member_instance_v<T>, T&> ISolo()
{
    return T::instance();
}

template<typename T>
std::enable_if_t<!has_class_member_instance_v<T>, T&> ISolo()
{
    static T instance;
    return instance;
}

$PackageWebCoreEnd
