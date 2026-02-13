#include "IRdbSqliteDialect.h"
#include "rdb/IRdbAbort.h"
#include "rdb/entity/IRdbTableInfo.h"

$PackageWebCoreBegin

QString IRdbSqliteDialect::databaseType() const
{
    return "Sqlite";
}

QString IRdbSqliteDialect::dropTableSql(const IRdbTableInfo &info) const
{
    return "DROP TABLE IF EXISTS " + quoteName(info.m_entityName);
}

QString IRdbSqliteDialect::getSqlType(const IRdbTableInfo& info, int index) const
{
    static const QMap<int, QString> map = {
        {QMetaType::Char, "INTEGER"},
        {QMetaType::UChar, "INTEGER"},
        {QMetaType::Short, "INTEGER"},
        {QMetaType::UShort, "INTEGER"},
        {QMetaType::Int, "INTEGER"},
        {QMetaType::UInt, "INTEGER"},
        {QMetaType::Long, "INTEGER"},
        {QMetaType::ULong, "INTEGER"},
        {QMetaType::LongLong, "INTEGER"},
        {QMetaType::ULongLong, "INTEGER"},
        {QMetaType::Double, "REAL"},
        {QMetaType::Float, "REAL"},
        {QMetaType::Bool, "BOOLEAN"},
        {QMetaType::QDate, "DATE"},
        {QMetaType::QTime, "TIME"},
        {QMetaType::QDateTime, "DATETIME"},
        {QMetaType::QString, "VARCHAR"},
        {qMetaTypeId<std::string>(), "VARCHAR"},
        {qMetaTypeId<IString>(), "VARCHAR"},
    };
    if(info.m_sqlType.contains(index)){
        return info.m_sqlType[index];
    }

    auto typeId = info.m_fields[index].m_typeId;
    if(!map.contains(typeId)){
        QString tip = QString("Type is not supported. Type:").append(IMetaUtil::typeName(typeId));
        IRdbAbort::abortDialectError(tip, $ISourceLocation);
    }
    return map[typeId];
}

$PackageWebCoreEnd
