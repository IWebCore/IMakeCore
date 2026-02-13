#include "IRdbTableInfo.h"

#include "rdb/IRdbAbort.h"
#include "rdb/IRdbManage.h"
#include "rdb/IRdbUtil.h"

$PackageWebCoreBegin

namespace detail
{
    void processIgnoredFields(const QMap<QString, QString> clsInfo, IRdbTableInfo& tableInfo);
    void processNotations(const QMap<QString, QString> clsInfo, IRdbTableInfo& tableInfo);
    bool setPrimaryKey(const QString& key, const QString& value, IRdbTableInfo& tableInfo);
    bool setUniqueKeys(const QString& key, const QString& value, IRdbTableInfo& tableInfo);
    bool setNotNullKeys(const QString& key, const QString& value, IRdbTableInfo& tableInfo);
    bool setAutoIncrementKeys(const QString& key, const QString& value, IRdbTableInfo& tableInfo);
    bool setSqlTypeKeys(const QString& key, const QString& value, IRdbTableInfo& tableInfo);
    bool setConstraintKeys(const QString& key, const QString& value, IRdbTableInfo& tableInfo);
    bool setInsertValueKeys(const QString& key, const QString& value, IRdbTableInfo& tableInfo);
    bool setGeneratValueKeys(const QString& key, const QString& value, IRdbTableInfo& tableInfo);
    bool setIgnoredValueKeys(const QString& key, const QString& value, IRdbTableInfo& tableInfo);

    void processChecks(const QMap<QString, QString>& clsInfo, const IRdbTableInfo& tableInfo);
    void checkFieldTypes(const QMap<QString, QString>& clsInfo, const IRdbTableInfo& tableInfo);
    void checkDuplicatedPrimaryKey(const QMap<QString, QString>& clsInfo, const IRdbTableInfo& tableInfo);
    void checkAutoGenerateInfo(const QMap<QString, QString>& clsInfo, const IRdbTableInfo& tableInfo);
}

IRdbTableInfo::IRdbTableInfo(const QMetaObject &meta) : IRdbEntityInfo(meta)
{
    auto clsInfo = IMetaUtil::getMetaClassInfoMap(meta);
    detail::processIgnoredFields(clsInfo, *this);
    detail::processNotations(clsInfo, *this);
    detail::processChecks(clsInfo, *this);

    for(int i=0; i<m_fields.size(); i++){
        m_valueMakers.append(ValueMaker{});
    }
}

void detail::processIgnoredFields(const QMap<QString, QString> clsInfo, IRdbTableInfo& tableInfo)
{
    for(const auto& name : clsInfo.keys()){
        detail::setIgnoredValueKeys(name, clsInfo[name], tableInfo);
    }
    // 移除 fields, fieldNames 等
    for(auto name : tableInfo.m_ignoredKeys){
        auto index = tableInfo.m_fieldNames.indexOf(name);
        tableInfo.m_fieldNames.removeAt(index);
        tableInfo.m_fields.removeAt(index);
    }
}

void detail::processNotations(const QMap<QString, QString> clsInfo, IRdbTableInfo& tableInfo)
{
    using NotationFun = std::function<bool(const QString&, const QString&, IRdbTableInfo&)>;
    static QList<NotationFun> notationFun = {
        detail::setPrimaryKey,
        detail::setUniqueKeys,
        detail::setNotNullKeys,
        detail::setAutoIncrementKeys,
        detail::setSqlTypeKeys,
        detail::setConstraintKeys,
        detail::setInsertValueKeys,
        detail::setGeneratValueKeys
    };

    for(const auto& name : clsInfo.keys()){
        for(auto fun : notationFun){
            if(fun(name, clsInfo[name], tableInfo)){
                break;
            }
        }
    }
}

bool detail::setPrimaryKey(const QString& key, const QString& value, IRdbTableInfo& tableInfo)
{
    static const char* const PREFIX = "sql_primaryKey__";
    if(key.startsWith(PREFIX)){
        auto index = tableInfo.m_fieldNames.indexOf(value);
        if(index == -1){
            QString tip = QString("Table: ").append(tableInfo.m_className)
                    .append(" Why: ").append("primary key incorrect");
            IRdbAbort::abortTableDeclarationError(tip, $ISourceLocation);
        }
        if(tableInfo.m_primaryKey != -1){
            QString tip = QString("Table: ").append(tableInfo.m_className)
                    .append(" Why: ").append("primary key already exist")
                    .append(" Field: ").append(value);
            IRdbAbort::abortTableDeclarationError(tip, $ISourceLocation);
        }
        tableInfo.m_primaryKey = index;
        return true;
    }
    return false;
}

bool detail::setUniqueKeys(const QString& key, const QString& value, IRdbTableInfo& tableInfo)
{
    static const char* const PREFIX = "sql_unique_key__";
    if(key.startsWith(PREFIX)){
        auto index = tableInfo.m_fieldNames.indexOf(value);
        if(index == -1){
            QString tip = QString("Table: ").append(tableInfo.m_className)
                    .append(" Why: ").append("error unique field names")
                    .append(" Field: ").append(value);
            IRdbAbort::abortTableDeclarationError(tip, $ISourceLocation);
        }
        tableInfo.m_uniqueKeys.append(index);
        return true;
    }
    return false;
}

bool detail::setNotNullKeys(const QString& key, const QString& value, IRdbTableInfo& tableInfo)
{
    static const char* const PREFIX = "sql_not_null_key__";
    if(key.startsWith(PREFIX)){
        auto index = tableInfo.m_fieldNames.indexOf(value);
        if(index == -1){
            QString tip = QString("Table: ").append(tableInfo.m_className)
                    .append(" Why: ").append("not null field not exist")
                    .append(" Field: ").append(value);
            IRdbAbort::abortTableDeclarationError(tip, $ISourceLocation);
        }
        tableInfo.m_notNullKeys.append(index);
        return true;
    }
    return false;
}

bool detail::setAutoIncrementKeys(const QString &key, const QString &value, IRdbTableInfo &tableInfo)
{
    static const char* const PREFIX = "sql_auto_increment__";
    if(key.startsWith(PREFIX)){
        auto index = tableInfo.m_fieldNames.indexOf(value);
        if(index == -1){
            QString tip = QString("Table: ").append(tableInfo.m_className)
                    .append(" Why: ").append("not exist auto_increment field")
                    .append(" Field: ").append(value);
            IRdbAbort::abortTableDeclarationError(tip, $ISourceLocation);
        }
        tableInfo.m_autoIncrement = index;
        return true;
    }
    return false;
}

bool detail::setSqlTypeKeys(const QString& key, const QString& value, IRdbTableInfo& tableInfo)
{
    static const char* const PREFIX = "sql_field_type__";
    if(key.startsWith(PREFIX)){
        auto fieldName = key.mid(QString(PREFIX).length());
        auto index = tableInfo.m_fieldNames.indexOf(fieldName);
        if(index == -1){
            QString tip = QString("Table: ").append(tableInfo.m_className)
                    .append(" Why: ").append("sql type not exist")
                    .append(" Field: ").append(value);
            IRdbAbort::abortTableDeclarationError(tip, $ISourceLocation);
        }
        if(tableInfo.m_sqlType.contains(index)){
            QString tip = QString("Table: ").append(tableInfo.m_className)
                    .append(" Why: ").append("sql type already exist")
                    .append(" Field: ").append(value);
            IRdbAbort::abortTableDeclarationError(tip, $ISourceLocation);
        }
        tableInfo.m_sqlType[index] = value;
        return true;
    }
    return false;
}

bool detail::setConstraintKeys(const QString &key, const QString &value, IRdbTableInfo &tableInfo)
{
    static const char* const PREFIX = "sql_column_constraint__";
    if(key.startsWith(PREFIX)){
        auto fieldName = key.mid(QString(PREFIX).length());
        auto index = tableInfo.m_fieldNames.indexOf(fieldName);
        if(index == -1){
            QString tip = QString("Table: ").append(tableInfo.m_className)
                    .append(" Why: ").append("sql constrait field not exist");
            IRdbAbort::abortTableDeclarationError(tip, $ISourceLocation);
        }
        if(tableInfo.m_constraints.contains(index)){
            QString tip = QString("Table: ").append(tableInfo.m_className)
                    .append(" Why: ").append("sql constrait in field already exist")
                    .append(" Field: ").append(value);
            IRdbAbort::abortTableDeclarationError(tip, $ISourceLocation);
        }
        tableInfo.m_constraints[index] = QString(value).replace("\"", "");
        return true;
    }
    return false;
}

bool detail::setInsertValueKeys(const QString& key, const QString& value, IRdbTableInfo& tableInfo)
{
    static const char* const PREFIX = "sql_insert_value__";
    if(key.startsWith(PREFIX)){
        auto fieldName = key.mid(QString(PREFIX).length());
        auto index = tableInfo.m_fieldNames.indexOf(fieldName);
        if(index == -1){
            QString tip = QString("Table: ").append(tableInfo.m_className)
                    .append(" Why: ").append("sql Insert value key field not exist")
                    .append(" Field: ").append(value);
            IRdbAbort::abortTableDeclarationError(tip, $ISourceLocation);
        }
        tableInfo.m_valueMakers[index].type = IRdbTableInfo::ValueMakerType::InsertValue;
        tableInfo.m_valueMakers[index].insertValue = value;
        return true;
    }
    return false;
}

bool detail::setGeneratValueKeys(const QString& key, const QString& value, IRdbTableInfo& tableInfo)
{
    static const char* const PREFIX = "sql_generate_value__";
    if(key.startsWith(PREFIX)){
        auto fieldName = key.mid(QString(PREFIX).length());
        auto index = tableInfo.m_fieldNames.indexOf(fieldName);
        if(index == -1){
            QString tip = QString("Table: ").append(tableInfo.m_className)
                    .append(" Why: ").append("sql constrait field not exist")
                    .append(" Field: ").append(value);
            IRdbAbort::abortTableDeclarationError(tip, $ISourceLocation);
        }
        tableInfo.m_valueMakers[index].type = IRdbTableInfo::ValueMakerType::GenerateValue;
        tableInfo.m_valueMakers[index].generator = IRdbManage::instance().getAutoGenerateKeyFunction(value);
        if(tableInfo.m_valueMakers[index].generator == nullptr){
            QString tip = QString("Table: ").append(tableInfo.m_className)
                    .append(" Why: ").append("no field generator exist")
                    .append(" Field: ").append(value);
            IRdbAbort::abortTableDeclarationError(tip, $ISourceLocation);
        }
        return true;
    }
    return false;
}

bool detail::setIgnoredValueKeys(const QString& key, const QString& value, IRdbTableInfo& tableInfo)
{
    static const char* const PREFIX = "sql_ignored_key__";
    if(key.startsWith(PREFIX)){
        auto index = tableInfo.m_fieldNames.indexOf(value);
        if(index == -1){
            QString tip = QString("Table: ").append(tableInfo.m_className)
                    .append(" Why: ").append("sql ignored field not exist")
                    .append(" Field: ").append(value);
            IRdbAbort::abortTableDeclarationError(tip, $ISourceLocation);
        }
        tableInfo.m_ignoredKeys.append(value);
        return true;
    }
    return false;
}

void detail::processChecks(const QMap<QString, QString> &clsInfo, const IRdbTableInfo &tableInfo)
{
    detail::checkFieldTypes(clsInfo, tableInfo);
    detail::checkDuplicatedPrimaryKey(clsInfo, tableInfo);
    detail::checkAutoGenerateInfo(clsInfo, tableInfo);
}

void detail::checkFieldTypes(const QMap<QString, QString> &clsInfo, const IRdbTableInfo& tableInfo)
{
    Q_UNUSED(clsInfo)
    static const QList<QMetaType::Type> allowTypes ={
        QMetaType::Bool,
        QMetaType::QString,
        QMetaType::Char, QMetaType::UChar,
        QMetaType::Short, QMetaType::UShort,
        QMetaType::Int, QMetaType::UInt,
        QMetaType::Long, QMetaType::ULong,
        QMetaType::LongLong, QMetaType::ULongLong,
        QMetaType::Double, QMetaType::Float,
        QMetaType::QDate, QMetaType::QTime, QMetaType::QDateTime,
        QMetaType::Type(qRegisterMetaType<IString>()),
        QMetaType::Type(qRegisterMetaType<std::string>())
    };

    for(const auto& field : tableInfo.m_fields){
        if(!allowTypes.contains(field.m_typeId) && !tableInfo.m_sqlType.contains(tableInfo.m_fieldNames.indexOf(field.m_name))){
            QString info = QString("this kind of type is not supported in table, please change to the supported type. \n"
                                   "Type : ").append(IMetaUtil::typeName(field.m_typeId));
            QString tip = QString("Table: ").append(tableInfo.m_className).append(" Why: ").append(info);
            IRdbAbort::abortTableDeclarationError(tip, $ISourceLocation);
        }
    }
}

void detail::checkDuplicatedPrimaryKey(const QMap<QString, QString> &clsInfo, const IRdbTableInfo& tableInfo)
{
    Q_UNUSED(clsInfo)
    if(tableInfo.m_primaryKey == -1){
        QString tip = QString("Table: ").append(tableInfo.m_className).append(" Why: ").append("table has no priamary key, please mark one");
        IRdbAbort::abortTableDeclarationError(tip, $ISourceLocation);
    }

    auto typeId = tableInfo.m_fields[tableInfo.m_primaryKey].m_typeId;
    if(!IRdbUtil::isPrimaryKeyType(typeId)){
        QString info = tableInfo.m_className + " table has incorrect primary key annotated type. \n"
                                   "the only allowed type is int, long, longlong/int64, QString\n"
                                   "field:" + tableInfo.m_fields[tableInfo.m_primaryKey].m_name + " type:" + tableInfo.m_fields[tableInfo.m_primaryKey].m_typeName;
        QString tip = QString("Table: ").append(tableInfo.m_className).append(" Why: ").append(info);
        IRdbAbort::abortTableDeclarationError(tip, $ISourceLocation);
    }

    if(typeId != QMetaType::QString && (typeId != QMetaType::LongLong) ){
        QString info = QString("primary key that is number type recommended is qlonglong/qint64 type.\n"
                               "current is ").append(IMetaUtil::typeName(typeId)).append(" in class ").append(tableInfo.m_className);
        qWarning() << info;
    }
}

void detail::checkAutoGenerateInfo(const QMap<QString, QString> &clsInfo, const IRdbTableInfo& tableInfo)
{
    Q_UNUSED(clsInfo)
    static const char* const Sql_AutoGenerateKeyClause = "autoIncrementKey__";
    static QList<QMetaType::Type> allowTypes = {
        QMetaType::Int, QMetaType::LongLong, QMetaType::QString
    };

    int index = 0;
    for(auto key : clsInfo.keys()){
        if(key.startsWith(Sql_AutoGenerateKeyClause)){
            index ++;
        }
    }
    if(index >1){
        QString info = tableInfo.m_className + " table: you can not have more than one increment note, please check";
        QString tip = QString("Table: ").append(tableInfo.m_className).append(" Why: ").append(info);
        IRdbAbort::abortTableDeclarationError(tip, $ISourceLocation);
    }
}

$PackageWebCoreEnd
