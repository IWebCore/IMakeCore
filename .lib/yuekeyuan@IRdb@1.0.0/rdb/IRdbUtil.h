#pragma once

#include "core/util/IHeaderUtil.h"
#include "core/base/IResult.h"
#include "rdb/entity/IRdbEntityInfo.h"
#include "rdb/ISqlQuery.h"

#if ! __has_include(<QtSql>)
    #error "IRdb package need Qt sql module support"
#endif

$PackageWebCoreBegin

//class ISqlQuery;
class IRdbTableInfo;
class IRdbEntityInfo;
class IRdbViewInfo;
namespace IRdbUtil
{
    namespace detail
    {
        void toBean(ISqlQuery& query, const QMetaObject& obj, void* ptr);
        void toEntity(ISqlQuery& query, const IRdbTableInfo& info, void* ptr);
        void toEntity(ISqlQuery& query, const IRdbViewInfo& info, void* ptr);
        void toEntity(ISqlQuery& query, QList<const IRdbEntityInfo::Field*> fields, void* ptr);
    }

    bool isPrimaryKeyType(QMetaType::Type type);

///////// single value
    int getInt(ISqlQuery& query, bool& ok);
    uint getUint(ISqlQuery& query, bool& ok);
    qulonglong getULongLong(ISqlQuery& query, bool& ok);
    qlonglong getLongLong(ISqlQuery& query, bool& ok);
    float getFloat(ISqlQuery& query, bool& ok);
    double getDouble(ISqlQuery& query, bool& ok);
    bool getBool(ISqlQuery& query, bool& ok);
    QDate getDate(ISqlQuery& query, bool& ok);
    QTime getTime(ISqlQuery& query, bool& ok);
    QDateTime getDateTime(ISqlQuery& query, bool& ok);
    QString getString(ISqlQuery& query, bool& ok);
    QVariant getVariant(ISqlQuery& query, bool& ok);
    QVariantMap getMap(ISqlQuery& query, bool& ok);

#define PP_GET_TYPE_VALUE( TYPE, FUNC )                      \
    TYPE FUNC (ISqlQuery& query, bool& ok);                  \
    inline IResult< TYPE > FUNC (ISqlQuery &query)           \
    {                                                        \
        bool ok{true};                                       \
        auto value =  FUNC (query, ok);                      \
        if(!ok){                                             \
            return std::nullopt;                             \
        }                                                    \
        return value;                                        \
    }
    PP_GET_TYPE_VALUE(int, getInt)
    PP_GET_TYPE_VALUE(uint, getUint)
    PP_GET_TYPE_VALUE(qlonglong, getLongLong)
    PP_GET_TYPE_VALUE(qulonglong, getULongLong)
    PP_GET_TYPE_VALUE(float, getFloat)
    PP_GET_TYPE_VALUE(double, getDouble)
    PP_GET_TYPE_VALUE(bool, getBool)
    PP_GET_TYPE_VALUE(QDate, getDate)
    PP_GET_TYPE_VALUE(QTime, getTime)
    PP_GET_TYPE_VALUE(QDateTime, getDateTime)
    PP_GET_TYPE_VALUE(QString, getString)
    PP_GET_TYPE_VALUE(QVariant, getVariant)
    PP_GET_TYPE_VALUE(QVariantMap, getMap)
#undef PP_GET_TYPE_VALUE

/////// list values;
    QVariantList getVariantList(ISqlQuery& query);
    QList<int> getIntList(ISqlQuery& query);
    QList<uint> getUintList(ISqlQuery& query);
    QList<qulonglong> getULongLongList(ISqlQuery& query);
    QList<qlonglong> getLongLongList(ISqlQuery& query);
    QList<float> getFloatList(ISqlQuery& query);
    QList<double> getDoubleList(ISqlQuery& query);
    QList<bool> getBoolList(ISqlQuery& query);
    QStringList getStringList(ISqlQuery& query);
    QList<QDate> getDateList(ISqlQuery& query);
    QList<QTime> getTimeList(ISqlQuery& query);
    QList<QDateTime> getDateTimeList(ISqlQuery& query);
    QList<QVariantMap> getVariantMapList(ISqlQuery& query);

//////// toXxx functions
    QList<int> toIntList(const QVariantList&);
    QList<uint> toUintList(const QVariantList&);
    QList<qulonglong> toULongLongList(const QVariantList&);
    QList<qlonglong> toLongLongList(const QVariantList&);
    QList<float> toFloatList(const QVariantList&);
    QList<double> toDoubleList(const QVariantList&);
    QList<bool> toBoolList(const QVariantList&);
    QStringList toStringList(const QVariantList&);
    QList<QDate> toDateList(const QVariantList&);
    QList<QTime> toTimeList(const QVariantList&);
    QList<QDateTime> toDateTimeList(const QVariantList&);

    template<typename T>
    IResult<T> getEntity(ISqlQuery& query);

    template <typename T>
    QList<T> getEntities(ISqlQuery& query);

    template<typename T>
    IResult<T> getBean(ISqlQuery& query);

    template<typename T>
    QList<T> getBeans(ISqlQuery& query);
}

template<typename T>
IResult<T> IRdbUtil::getEntity(ISqlQuery& query)
{
    bool exist{false};
    T t;
    while(query.next()){
        if(exist){
            return std::nullopt;
        }
        detail::toEntity(query, T::staticEntityInfo(), &t);
        exist = true;
    }
    if(exist){
        return t;
    }
    return std::nullopt;
}

template<typename T>
IResult<T> IRdbUtil::getBean(ISqlQuery& query)
{
    bool exist{false};
    T t;
    while(query.next()){
        if(exist){
            return std::nullopt;
        }
        detail::toBean(query, T::staticMetaObject, &t);
        exist = true;
    }

    if(exist){
        return t;
    }
    return std::nullopt;
}

template<class T>
QList<T> IRdbUtil::getEntities(ISqlQuery &query)
{
    const IRdbEntityInfo& info = T::staticEntityInfo();
    QList<T> beans;
    bool isFieldReady{false};
    QList<const IRdbEntityInfo::Field*> fields;
    while(query.next()){
        if(!isFieldReady){
            const auto& record = query.record();
            for(const auto& field : info.m_fields){
                if(record.contains(field.m_name)){
                    fields.append(&field);
                }
            }
            isFieldReady = true;
        }

        T t;
        detail::toEntity(query, fields, &t);
        beans.append(t);
    }
    return beans;
}

template<class T>
QList<T> IRdbUtil::getBeans(ISqlQuery &query)
{
    const auto& metaInfo = T::staticMetaObject;
    QList<T> beans;
    while(query.next()){
        T bean;
        beans.append(detail::toBean(query, metaInfo, &bean));
    }
    return beans;
}

$PackageWebCoreEnd
