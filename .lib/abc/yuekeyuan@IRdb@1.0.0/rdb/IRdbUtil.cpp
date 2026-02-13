#include "IRdbUtil.h"
#include "core/util/IConvertUtil.h"
#include "rdb/exception/IRdbException.h"
#include "rdb/IRdbAbort.h"
#include "rdb/ISqlQuery.h"
#include "rdb/entity/IRdbTableInfo.h"
#include "rdb/entity/IRdbEntityInfo.h"
#include "rdb/entity/IRdbViewInfo.h"

$PackageWebCoreBegin

namespace detail
{
    QStringList getFieldNames(const QSqlRecord& record)
    {
        QStringList ret;
        for(auto index=0; index < record.count(); index++){
            ret.append(record.fieldName(index));
        }
        return ret;
    }

    QVariant getSingleValue(ISqlQuery& query, bool& ok)
    {
        int count = 0;
        QVariant ret;       // this is invalid variant
        while(query.next()){
            if((count >= 1) || (query.record().count() != 1)){
                ok = false;
                return ret;
            }
            if(query.record().count() != 1){
                throw IRdbException("query column should be only one");
            }
            ret = query.value(0);
            count ++;
        }
        if(count == 0){
            ok = false;
            return QVariant{};
        }
        ok = true;
        return ret;
    }

    QVariantList getListValues(ISqlQuery& query)
    {
        QVariantList ret;

        bool flag{false};
        while(query.next()){
            if(!flag){
                if(query.record().count() != 1){
                    throw IRdbException("query count should be only one");
                }
                flag = true;
            }
            ret.append(query.value(0));
        }
        return ret;
    }

    QVariantMap getOneVariantMap(ISqlQuery& query, bool& ok)
    {
        QVariantMap ret;
        int count = 0;
        while(query.next()){
            if(count >= 1){
                ok = false;
                return ret;
            }
            auto record = query.record();
            auto recordCount = record.count();
            for(int i=0; i<recordCount; i++){
                auto name = record.fieldName(i);
                ret[name] = query.value(i);
            }
            count ++;
        }
        if(count == 0){
            ok = false;
            return ret;
        }
        ok = true;
        return ret;
    }

    QList<QVariantMap> getVariantMapList(ISqlQuery& query)
    {
        QList<QVariantMap> ret;

        bool flag{false};
        QStringList names;
        while(query.next()){
            if(!flag){
                names = ::detail::getFieldNames(query.record());
                flag = true;
            }

            QVariantMap map;
            for(const auto& name : names){
                map[name] = query.value(name);
            }
            ret.append(map);
        }
        return ret;
    }
}

bool IRdbUtil::isPrimaryKeyType(QMetaType::Type type)
{
    static const QList<QMetaType::Type> PrimaryKeyTypes = {
        QMetaType::Int,
        QMetaType::Long,
        QMetaType::LongLong,
        QMetaType::QString
    };

    return PrimaryKeyTypes.indexOf(type) != -1;
}

void IRdbUtil::detail::toEntity(ISqlQuery &query, const IRdbTableInfo &info, void *ptr)
{
    auto names = ::detail::getFieldNames(query.record());
    for(const auto& field : info.m_fields){
        if(names.contains(field.m_name)){
            IMetaUtil::writeProperty(field.m_property, ptr, query.value(field.m_name));
        }
    }
}

void IRdbUtil::detail::toEntity(ISqlQuery &query, const IRdbViewInfo &info, void *ptr)
{
    auto names = ::detail::getFieldNames(query.record());
    for(const auto& field : info.m_fields){
        if(names.contains(field.m_name)){
            IMetaUtil::writeProperty(field.m_property, ptr, query.value(field.m_name));
        }
    }
}

void IRdbUtil::detail::toBean(ISqlQuery &query, const QMetaObject &obj, void *ptr)
{
    auto names = ::detail::getFieldNames(query.record());
    auto count = obj.propertyCount();
    for(int i=0; i<count; i++){
        const auto& name = obj.property(i).name();
        if(names.contains(obj.property(i).name())){
            IMetaUtil::writeProperty(obj.property(i), ptr, query.value(name));
        }
    }
}

void IRdbUtil::detail::toEntity(ISqlQuery &query, QList<const IRdbEntityInfo::Field*> fields, void* ptr)
{
    for(const auto& field : fields){
        IMetaUtil::writeProperty(field->m_property, ptr, query.value(field->m_name));
    }
}

int IRdbUtil::getInt(ISqlQuery &query, bool& ok)
{
    auto val = ::detail::getSingleValue(query, ok);
    if(ok){
        return val.toInt(&ok);
    }
    return {};
}

uint IRdbUtil::getUint(ISqlQuery &query, bool& ok)
{
    auto val = ::detail::getSingleValue(query, ok);
    if(ok){
        return val.toUInt(&ok);
    }
    return {};
}

qulonglong IRdbUtil::getULongLong(ISqlQuery &query, bool& ok)
{
    auto val = ::detail::getSingleValue(query, ok);
    if(ok){
        return val.toULongLong(&ok);
    }
    return {};
}

qlonglong IRdbUtil::getLongLong(ISqlQuery &query, bool& ok)
{
    auto val = ::detail::getSingleValue(query, ok);
    if(ok){
        return val.toLongLong(&ok);
    }
    return {};
}

float IRdbUtil::getFloat(ISqlQuery &query, bool& ok)
{
    auto val = ::detail::getSingleValue(query, ok);
    if(ok){
        return val.toFloat(&ok);
    }
    return {};
}

double IRdbUtil::getDouble(ISqlQuery &query, bool& ok)
{
    auto val = ::detail::getSingleValue(query, ok);
    if(ok){
        return val.toDouble(&ok);
    }
    return {};
}

bool IRdbUtil::getBool(ISqlQuery &query, bool& ok)
{
    auto val = ::detail::getSingleValue(query, ok);
    if(ok){
        return val.toBool();
    }
    return {};
}

QDate IRdbUtil::getDate(ISqlQuery &query, bool& ok)
{
    auto val = ::detail::getSingleValue(query, ok);
    if(!ok){
        return QDate();
    }

    switch (IMetaUtil::typeId(val)) {
    case QMetaType::QDate:
        return val.toDate();
    case QMetaType::QDateTime:
        return val.toDateTime().date();
    case QMetaType::QString:
        return IConvertUtil::toDate(val.toString(), ok);
    case QMetaType::UnknownType:
        return QDate();
    default:
        IRdbAbort::abortRdbUtilError("date convertion error", $ISourceLocation);
    }
    return QDate();
}

QTime IRdbUtil::getTime(ISqlQuery &query,  bool& ok)
{
    auto val = ::detail::getSingleValue(query, ok);
    if(!ok){
        return {};
    }

    switch (IMetaUtil::typeId(val)) {
    case QMetaType::QTime:
        return val.toTime();
    case QMetaType::QDateTime:
        return val.toDateTime().time();
    case QMetaType::QString:
        return IConvertUtil::toTime(val.toString(), ok);
    case QMetaType::UnknownType:
        return QTime();
    default:
        IRdbAbort::abortRdbUtilError("time convertion error", $ISourceLocation);
    }
    return QTime();
}

QDateTime IRdbUtil::getDateTime(ISqlQuery &query, bool& ok)
{
    auto val = ::detail::getSingleValue(query, ok);
    if(!ok){
        return {};
    }
    switch (IMetaUtil::typeId(val)) {
    case QMetaType::QDateTime:
        return val.toDateTime();
    case QMetaType::QString:
        return IConvertUtil::toDateTime(val.toString(), ok);
    case QMetaType::UnknownType:
        return QDateTime();
    default:
        IRdbAbort::abortRdbUtilError("DateTime convertion erorr", $ISourceLocation);
    }
    return QDateTime();
}

QString IRdbUtil::getString(ISqlQuery &query, bool& ok)
{
    auto val = ::detail::getSingleValue(query, ok);
    if(ok){
        return val.toString();
    }
    return {};
}

QVariant IRdbUtil::getVariant(ISqlQuery &query, bool& ok)
{
    return ::detail::getSingleValue(query, ok);
}

QVariantMap IRdbUtil::getMap(ISqlQuery &query, bool& ok)
{
    return ::detail::getOneVariantMap(query, ok);
}

QVariantList IRdbUtil::getVariantList(ISqlQuery &query)
{
    return ::detail::getListValues(query);
}

QList<int> IRdbUtil::getIntList(ISqlQuery &query)
{
    auto result = ::detail::getListValues(query);
    return toIntList(result);
}

QList<uint> IRdbUtil::getUintList(ISqlQuery &query)
{
    auto result = ::detail::getListValues(query);
    return toUintList(result);
}

QList<qulonglong> IRdbUtil::getULongLongList(ISqlQuery &query)
{
    auto result = ::detail::getListValues(query);
    return toULongLongList(result);
}

QList<qlonglong> IRdbUtil::getLongLongList(ISqlQuery &query)
{
    auto result = ::detail::getListValues(query);
    return toLongLongList(result);
}

QList<float> IRdbUtil::getFloatList(ISqlQuery &query)
{
    auto result = ::detail::getListValues(query);
    return toFloatList(result);
}

QList<double> IRdbUtil::getDoubleList(ISqlQuery &query)
{
    auto result = ::detail::getListValues(query);
    return toDoubleList(result);
}

QList<bool> IRdbUtil::getBoolList(ISqlQuery &query)
{
    auto result = ::detail::getListValues(query);
    return toBoolList(result);
}

QStringList IRdbUtil::getStringList(ISqlQuery &query)
{
    auto result = ::detail::getListValues(query);
    return toStringList(result);
}

QList<QDate> IRdbUtil::getDateList(ISqlQuery &query)
{
    auto result = ::detail::getListValues(query);
    return toDateList(result);
}

QList<QTime> IRdbUtil::getTimeList(ISqlQuery &query)
{
    auto result = ::detail::getListValues(query);
    return toTimeList(result);
}

QList<QDateTime> IRdbUtil::getDateTimeList(ISqlQuery &query)
{
    auto result = ::detail::getListValues(query);
    return toDateTimeList(result);
}

QList<QVariantMap> IRdbUtil::getVariantMapList(ISqlQuery &query)
{
    QList<QVariantMap> ret;

    QStringList fieldNames;
    bool flag{false};
    while(query.next()){
        if(!flag){
            fieldNames = ::detail::getFieldNames(query.record());
            flag = true;
        }
        QVariantMap map;
        for(const auto& field : fieldNames){
            map[field] = query.value(field);
        }
        ret.append(map);
    }
    return ret;
}

QList<int> IRdbUtil::toIntList(const QVariantList& result)
{
    bool ok;
    QList<int> ret;
    for(const auto& val : result){
        ret.append(val.toInt(&ok));
        if(!ok){
            throw IRdbException("convert failed");
        }
    }
    return ret;
}

QList<uint> IRdbUtil::toUintList(const QVariantList& result)
{
    bool ok;
    QList<uint> ret;
    for(const auto& val : result){
        ret.append(val.toUInt(&ok));
        if(!ok){
            throw IRdbException("convert failed");
        }
    }
    return ret;
}

QList<qulonglong> IRdbUtil::toULongLongList(const QVariantList& result)
{
    bool ok;
    QList<qulonglong> ret;
    for(const auto& val : result){
        ret.append(val.toULongLong(&ok));
        if(!ok){
            throw IRdbException("convert failed");
        }
    }
    return ret;
}

QList<qlonglong> IRdbUtil::toLongLongList(const QVariantList& result)
{
    bool ok;
    QList<qlonglong> ret;
    for(const auto& val : result){
        ret.append(val.toLongLong(&ok));
        if(!ok){
            throw IRdbException("convert failed");
        }
    }
    return ret;
}

QList<float> IRdbUtil::toFloatList(const QVariantList& result)
{
    bool ok;
    QList<float> ret;
    for(const auto& val : result){
        ret.append(val.toFloat(&ok));
        if(!ok){
            throw IRdbException("convert failed");
        }
    }
    return ret;
}

QList<double> IRdbUtil::toDoubleList(const QVariantList& result)
{
    bool ok;
    QList<double> ret;
    for(const auto& val : result){
        ret.append(val.toDouble(&ok));
        if(!ok){
            throw IRdbException("convert failed");
        }
    }
    return ret;
}

QList<bool> IRdbUtil::toBoolList(const QVariantList& result)
{
    bool ok;
    QList<bool> ret;
    for(const auto& val : result){
        auto value = val.toInt(&ok);
        ret.append(value != 0);
        if(!ok){
            throw IRdbException("convert failed");
        }
    }
    return ret;
}

QStringList IRdbUtil::toStringList(const QVariantList& result)
{
    QStringList ret;
    for(const auto& val : result){
        ret.append(val.toString());
    }
    return ret;
}

QList<QDate> IRdbUtil::toDateList(const QVariantList& result)
{
    bool ok;
    QList<QDate> dates;
    for(const QVariant& val : result){
        switch (IMetaUtil::typeId(val)) {
        case QMetaType::QDate:
            dates.append(val.toDate());
            break;
        case QMetaType::QDateTime:
            dates.append(val.toDateTime().date());
            break;
        case QMetaType::QString:
            dates.append(IConvertUtil::toDate(val.toString(), ok));
            if(!ok){
                throw IRdbException("convert failed");
            }
            break;
        case QMetaType::UnknownType:
            dates.append(QDate());
            break;
        default:
            IRdbAbort::abortRdbUtilError("currently other type of date not supported", $ISourceLocation);
        }
    }
    return dates;
}

QList<QTime> IRdbUtil::toTimeList(const QVariantList& result)
{
    bool ok;
    QList<QTime> ret;
    for(const QVariant& val : result){
        switch (IMetaUtil::typeId(val)) {
        case QMetaType::Type::QDateTime:
            ret.append(val.toDateTime().time());
            break;
        case QMetaType::Type::QTime:
            ret.append(val.toTime());
            break;
        case QMetaType::Type::QString:
            ret.append(IConvertUtil::toTime(val.toString(), ok));
            if(!ok){
                throw IRdbException("convert failed");
            }
            break;
        case QMetaType::Type::UnknownType:
            ret.append(QTime());
            break;
        default:
            IRdbAbort::abortRdbUtilError("currently other type of time not supported", $ISourceLocation);
        }
    }
    return ret;
}

QList<QDateTime> IRdbUtil::toDateTimeList(const QVariantList& result)
{
    bool ok;
    QList<QDateTime> ret;
    for(const QVariant& val : result){
        switch (IMetaUtil::typeId(val)) {
        case QMetaType::QDateTime:
            ret.append(val.toDateTime());
            break;
        case QMetaType::QString:
            ret.append(IConvertUtil::toDateTime(val.toString(), ok));
            if(!ok){
                throw IRdbException("convert failed");
            }
            break;
        case QMetaType::UnknownType:
            ret.append(QDateTime());
            break;
        default:
            IRdbAbort::abortRdbUtilError("currently other type of DateTime not supported", $ISourceLocation);
        }
    }
    return ret;
}

$PackageWebCoreEnd
