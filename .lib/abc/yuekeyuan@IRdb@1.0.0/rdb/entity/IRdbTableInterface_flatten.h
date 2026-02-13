#pragma once

#ifdef IWEBCORE_FLATTEN_CRTP

#include "core/bean/detail/IBeanInterfaceDetail.h"
#include "core/util/IHeaderUtil.h"
#include "rdb/entity/IRdbTableInfo.h"
#include "rdb/pp/IRdbTablePreProcessor.h"
#include "core/task/unit/ITaskInstantUnit.h"

$PackageWebCoreBegin

template<typename T, bool enabled=true, IBeanTrait trait = IBeanTrait::Tolerance>
class IRdbTableInterface // : public IBeanInterface<T, enabled, trait>
{
    $AsTaskUnit(IRdbTableInterface)
public:
    IRdbTableInterface() = default;
    virtual ~IRdbTableInterface() = default;

public:
    void $task();

public:
    static const IRdbTableInfo& staticEntityInfo();

public:
    virtual IJson toJson() const;
    virtual bool loadJson(const IJson &value, const IBeanTrait& = trait);
    static IResult<T> fromJson(const IJson& value, const IBeanTrait& = trait);

private:
    static void registBean();
    static void registQList();
    static void registStdList();
    static void registQVector();
    static void registStdVector();

    static void registQStringQMap();
    static void registStdStringQMap();
    static void registIStringQMap();
    static void registQStringStdMap();
    static void registStdStringStdMap();
    static void registIStringStdMap();
};

template<typename T, bool enabled, IBeanTrait trait>
const IRdbTableInfo& IRdbTableInterface<T, enabled, trait>::staticEntityInfo()
{
    static IRdbTableInfo s_info(T::staticMetaObject);
    return s_info;
}


template<typename T, bool enabled, IBeanTrait trait>
IJson IRdbTableInterface<T, enabled, trait>::toJson() const
{
    static const auto methodMap = detail::getMethodMap(T::staticMetaObject);
    return detail::processToJson(this, methodMap);
}

template<typename T, bool enabled, IBeanTrait trait>
bool IRdbTableInterface<T, enabled, trait>::loadJson(const IJson &value, const IBeanTrait& beanTrait)
{
    static const auto required = detail::getRequiredMethodMap(T::staticMetaObject);
    static const auto optional = detail::getOptionalMethodMap(T::staticMetaObject);
    static const auto fieldNames = detail::getFieldNames(T::staticMetaObject);
    static const auto validator = detail::getJsonValidatorMethod(T::staticMetaObject);
    return detail::processLoadJson(this, value, beanTrait, required, optional, fieldNames, validator);
}

template<typename T, bool enabled, IBeanTrait trait>
IResult<T> IRdbTableInterface<T, enabled, trait>::fromJson(const IJson& value, const IBeanTrait& beanTrait)
{
    T t;
    if(t.loadJson(value, beanTrait)){
        return t;
    }
    return std::nullopt;
}

template<typename T, bool enabled, IBeanTrait trait>
void IRdbTableInterface<T, enabled, trait>::$task()
{
    registBean();
    registQList();
    registStdList();
    registQVector();
    registStdVector();

    registQStringQMap();
    registStdStringQMap();
    registIStringQMap();

    registQStringStdMap();
    registStdStringStdMap();
    registIStringStdMap();
}

template<typename T, bool enabled, IBeanTrait trait>
void IRdbTableInterface<T, enabled, trait>::registBean()
{
    auto ids = IMetaUtil::registMetaType<T>();
    for(auto id : ids){
        IBeanTypeManage::instance().registBeanId(id);
        IBeanTypeManage::instance().registBeanFromJsonFun(id,[](void* ptr, const IJson& json)->bool{
            return IJsonUtil::fromJson(*static_cast<T*>(ptr), json);
        });
        IBeanTypeManage::instance().registBeanToJsonFun(id, [](void* ptr)->IJson{
            return IJsonUtil::toJson(*static_cast<T*>(ptr));
        });
    }
}

template<typename T, bool enabled, IBeanTrait trait>
void IRdbTableInterface<T, enabled, trait>::registQList()
{
    auto name = "QList<" + IMetaUtil::getTypeName<T>() + ">";
    auto ids = IMetaUtil::registMetaType<QList<T>>({name});
    for(auto id : ids){
        IBeanTypeManage::instance().registBeanId(id);
        IBeanTypeManage::instance().registBeanFromJsonFun(id,[](void* ptr, const IJson& json)->bool{
            return IJsonUtil::fromJson(*static_cast<QList<T>*>(ptr), json);
        });
        IBeanTypeManage::instance().registBeanToJsonFun(id, [](void* ptr)->IJson{
            return IJsonUtil::toJson(*static_cast<QList<T>*>(ptr));
        });
    }
}

template<typename T, bool enabled, IBeanTrait trait>
void IRdbTableInterface<T, enabled, trait>::registStdList()
{
    auto name = "std::list<" + IMetaUtil::getTypeName<T>() + ">";
    auto ids = IMetaUtil::registMetaType< std::list<T> >({name});
    for(auto id : ids){
        IBeanTypeManage::instance().registBeanId(id);
        IBeanTypeManage::instance().registBeanFromJsonFun(id,[](void* ptr, const IJson& json)->bool{
            return IJsonUtil::fromJson(*static_cast< std::list<T>*>(ptr), json);
        });
        IBeanTypeManage::instance().registBeanToJsonFun(id, [](void* ptr)->IJson{
            return IJsonUtil::toJson(*static_cast< std::list<T>*>(ptr));
        });
    }
}

template<typename T, bool enabled, IBeanTrait trait>
void IRdbTableInterface<T, enabled, trait>::registQVector()
{
    auto name = "QVector<" + IMetaUtil::getTypeName<T>() + ">";
    auto ids = IMetaUtil::registMetaType<QVector<T>>({name});
    for(auto id : ids){
        IBeanTypeManage::instance().registBeanId(id);
        IBeanTypeManage::instance().registBeanFromJsonFun(id,[](void* ptr, const IJson& json)->bool{
            return IJsonUtil::fromJson(*static_cast<QVector<T>*>(ptr), json);
        });
        IBeanTypeManage::instance().registBeanToJsonFun(id, [](void* ptr)->IJson{
            return IJsonUtil::toJson(*static_cast<QVector<T>*>(ptr));
        });
    }
}

template<typename T, bool enabled, IBeanTrait trait>
void IRdbTableInterface<T, enabled, trait>::registStdVector()
{
    auto name = "std::vector<" + IMetaUtil::getTypeName<T>() + ">";
    auto ids = IMetaUtil::registMetaType<std::vector<T>>({name});
    for(auto id : ids){
        IBeanTypeManage::instance().registBeanId(id);
        IBeanTypeManage::instance().registBeanFromJsonFun(id,[](void* ptr, const IJson& json)->bool{
            return IJsonUtil::fromJson(*static_cast<std::vector<T>*>(ptr), json);
        });
        IBeanTypeManage::instance().registBeanToJsonFun(id, [](void* ptr)->IJson{
            return IJsonUtil::toJson(*static_cast<std::vector<T>*>(ptr));
        });
    }
}

template<typename T, bool enabled, IBeanTrait trait>
void IRdbTableInterface<T, enabled, trait>::registQStringQMap()
{
    auto name = "QMap<QString, " + IMetaUtil::getTypeName<T>() + ">";
    auto ids = IMetaUtil::registMetaType<QMap<QString, T>>({name});
    for(auto id : ids){
        IBeanTypeManage::instance().registBeanId(id);
        IBeanTypeManage::instance().registBeanFromJsonFun(id,[](void* ptr, const IJson& json)->bool{
            return IJsonUtil::fromJson(*static_cast<QMap<QString, T>*>(ptr), json);
        });
        IBeanTypeManage::instance().registBeanToJsonFun(id, [](void* ptr)->IJson{
            return IJsonUtil::toJson(*static_cast<QMap<QString, T>*>(ptr));
        });
    }
}

template<typename T, bool enabled, IBeanTrait trait>
void IRdbTableInterface<T, enabled, trait>::registStdStringQMap()
{
    auto name = "QMap<std::string, " + IMetaUtil::getTypeName<T>() + ">";
    auto ids = IMetaUtil::registMetaType<QMap<std::string, T>>({name});
    for(auto id : ids){
        IBeanTypeManage::instance().registBeanId(id);
        IBeanTypeManage::instance().registBeanFromJsonFun(id,[](void* ptr, const IJson& json)->bool{
            return IJsonUtil::fromJson(*static_cast<QMap<std::string, T>*>(ptr), json);
        });
        IBeanTypeManage::instance().registBeanToJsonFun(id, [](void* ptr)->IJson{
            return IJsonUtil::toJson(*static_cast<QMap<std::string, T>*>(ptr));
        });
    }
}

template<typename T, bool enabled, IBeanTrait trait>
void IRdbTableInterface<T, enabled, trait>::registIStringQMap()
{
    auto name = "QMap<IString, " + IMetaUtil::getTypeName<T>() + ">";
    auto ids = IMetaUtil::registMetaType<QMap<IString, T>>({name});
    for(auto id : ids){
        IBeanTypeManage::instance().registBeanId(id);
        IBeanTypeManage::instance().registBeanFromJsonFun(id,[](void* ptr, const IJson& json)->bool{
            return IJsonUtil::fromJson(*static_cast<QMap<IString, T>*>(ptr), json);
        });
        IBeanTypeManage::instance().registBeanToJsonFun(id, [](void* ptr)->IJson{
            return IJsonUtil::toJson(*static_cast<QMap<IString, T>*>(ptr));
        });
    }
}

template<typename T, bool enabled, IBeanTrait trait>
void IRdbTableInterface<T, enabled, trait>::registQStringStdMap()
{
    auto name = "std::map<QString, " + IMetaUtil::getTypeName<T>() + ">";
    auto ids = IMetaUtil::registMetaType<std::map<QString, T>>({name});
    for(auto id : ids){
        IBeanTypeManage::instance().registBeanId(id);
        IBeanTypeManage::instance().registBeanFromJsonFun(id,[](void* ptr, const IJson& json)->bool{
            return IJsonUtil::fromJson(*static_cast<std::map<QString, T>*>(ptr), json);
        });
        IBeanTypeManage::instance().registBeanToJsonFun(id, [](void* ptr)->IJson{
            return IJsonUtil::toJson(*static_cast<std::map<QString, T>*>(ptr));
        });
    }
}

template<typename T, bool enabled, IBeanTrait trait>
void IRdbTableInterface<T, enabled, trait>::registStdStringStdMap()
{
    auto name = "std::map<std::string, " + IMetaUtil::getTypeName<T>() + ">";
    auto ids = IMetaUtil::registMetaType<std::map<std::string, T>>({name});
    for(auto id : ids){
        IBeanTypeManage::instance().registBeanId(id);
        IBeanTypeManage::instance().registBeanFromJsonFun(id,[](void* ptr, const IJson& json)->bool{
            return IJsonUtil::fromJson(*static_cast<std::map<std::string, T>*>(ptr), json);
        });
        IBeanTypeManage::instance().registBeanToJsonFun(id, [](void* ptr)->IJson{
            return IJsonUtil::toJson(*static_cast<std::map<std::string, T>*>(ptr));
        });
    }
}

template<typename T, bool enabled, IBeanTrait trait>
void IRdbTableInterface<T, enabled, trait>::registIStringStdMap()
{
    auto name = "std::map<IString, " + IMetaUtil::getTypeName<T>() + ">";
    auto ids = IMetaUtil::registMetaType<std::map<IString, T>>({name});
    for(auto id : ids){
        IBeanTypeManage::instance().registBeanId(id);
        IBeanTypeManage::instance().registBeanFromJsonFun(id,[](void* ptr, const IJson& json)->bool{
            return IJsonUtil::fromJson(*static_cast<std::map<IString, T>*>(ptr), json);
        });
        IBeanTypeManage::instance().registBeanToJsonFun(id, [](void* ptr)->IJson{
            return IJsonUtil::toJson(*static_cast<std::map<IString, T>*>(ptr));
        });
    }
}

template<typename T, bool enabled, IBeanTrait trait>
typename IRdbTableInterface<T, enabled, trait>::IRdbTableInterfaceInitPrivate IRdbTableInterface<T, enabled, trait>::m_private;

template<typename T, bool enabled, IBeanTrait trait>
IRdbTableInterface<T, enabled, trait>::IRdbTableInterfaceInitPrivate::IRdbTableInterfaceInitPrivate()
{
    if constexpr (enabled){
        static std::once_flag flag;
        std::call_once(flag, []{
            static_cast<IRdbTableInterface&>(ISolo<T>()).$task();
        });
    }
}

$PackageWebCoreEnd

#endif
