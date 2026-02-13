#include "IRdbMysqlDialect.h"
#include "rdb/IRdbAbort.h"
#include "rdb/ISqlQuery.h"
#include "rdb/entity/IRdbTableInfo.h"

$PackageWebCoreBegin

QString IRdbMysqlDialect::databaseType() const
{
    return "MySql";
}

QString IRdbMysqlDialect::getSqlType(const IRdbTableInfo &info, int index) const
{
    static const QMap<int, QString> map = {
        {QMetaType::Char, "TINYINT"},
        {QMetaType::UChar, "TINYINT UNSIGNED "},
        {QMetaType::Short, "SMALLINT"},
        {QMetaType::UShort, "SMALLINT UNSIGNED"},
        {QMetaType::Int, "INT"},
        {QMetaType::UInt, "INT UNSIGNED"},
        {QMetaType::Long, "BIGINT"},
        {QMetaType::ULong, "BIGINT UNSIGNED"},
        {QMetaType::LongLong, "BIGINT"},
        {QMetaType::ULongLong, "BIGINT UNSIGNED"},
        {QMetaType::Double, "DOUBLE"},
        {QMetaType::Float, "FLOAT"},
        {QMetaType::Bool, "TINYINT(1)"},
        {QMetaType::QDate, "DATE"},
        {QMetaType::QTime, "TIME"},
        {QMetaType::QDateTime, "DATETIME"},
        {QMetaType::QString, "VARCHAR(255)"},
        {qMetaTypeId<std::string>(), "VARCHAR(255)"},
        {qMetaTypeId<IString>(), "VARCHAR(255)"},
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

QString IRdbMysqlDialect::createSqlCommonKeyClause(const IRdbTableInfo &info, int index) const
{
    const auto& name = info.m_fieldNames[index];
    auto sqlType = getSqlType(info, index);

    QString piece = name + " " + sqlType;
    if(info.m_notNullKeys.contains(index)){
        piece.append(" NOT NULL");
    }
    if(info.m_uniqueKeys.contains(index)){
        piece.append(" UNIQUE");
    }
    if(info.m_primaryKey == index){
        piece.append(" PRIMARY KEY");
    }
    if(info.m_autoIncrement == index){
        piece.append(" AUTO_INCREMENT");
    }
    if(info.m_constraints.contains(index)){
        piece.append(" ").append(info.m_constraints[index]);
    }
    return piece;
}

QString IRdbMysqlDialect::quoteName(const QString &name) const
{
    return "`" + name + "`";
}

$PackageWebCoreEnd
