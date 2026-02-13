#include "IRdbSqlServerDialect.h"
#include "rdb/IRdbAbort.h"
#include "rdb/ISqlQuery.h"
#include "rdb/clause/IRdbLimitClause.h"
#include "rdb/entity/IRdbTableInfo.h"

$PackageWebCoreBegin

QString IRdbSqlServerDialect::databaseType() const
{
    return "SqlServer";
}

QString IRdbSqlServerDialect::createTableSql(const IRdbTableInfo &info) const
{
    QStringList fields;
    for (auto index = 0; index < info.m_fields.length(); index++) {
        fields.append(createSqlCommonKeyClause(info, index));
    }

    return QString("CREATE TABLE ")
            .append(info.m_entityName)
            .append(" (").append(fields.join(", ") + ')');
}

QString IRdbSqlServerDialect::dropTableSql(const IRdbTableInfo &info) const
{
    return "DROP TABLE IF EXISTS " + quoteName(info.m_entityName);
}

QString IRdbSqlServerDialect::getSqlType(const IRdbTableInfo &info, int index) const
{
    static const QMap<int, QString> map = {
        {QMetaType::Char, "smallint"},
        {QMetaType::UChar, "tinyint"},
        {QMetaType::Short, "smallint"},
        {QMetaType::UShort, "int"},
        {QMetaType::Int, "int"},
        {QMetaType::UInt, "bigint"},
        {QMetaType::Long, "bigint"},
        {QMetaType::ULong, "bigint"},
        {QMetaType::LongLong, "bigint"},
        {QMetaType::ULongLong, "bigint"},
        {QMetaType::Double, "float"},
        {QMetaType::Float, "real"},
        {QMetaType::Bool, "bit"},
        {QMetaType::QDate, "date"},
        {QMetaType::QTime, "time"},
        {QMetaType::QDateTime, "datetime"},
        {QMetaType::QString, "varchar(255)"},
        {qMetaTypeId<std::string>(), "varchar(255)"},
        {qMetaTypeId<IString>(), "varchar(255)"},
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

QString IRdbSqlServerDialect::createSqlCommonKeyClause(const IRdbTableInfo &info, int index) const
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
        piece.append(" IDENTITY(1,1)");
    }
    if(info.m_constraints.contains(index)){
        piece.append(" ").append(info.m_constraints[index]);
    }
    return piece;
}

QString IRdbSqlServerDialect::fromLimitClause(const IRdbLimitClause &limit) const
{
    if(limit.m_limit < 0){
        return {};
    }

    QString sql;
    if(limit.m_offset >0){
        sql += " OFFSET " + QString::number(limit.m_offset) + " ROWS";
    }

    sql += " FETCH NEXT " + QString::number(limit.m_limit) + " ROWS ONLY";
    return sql;
}

void IRdbSqlServerDialect::bindParameter(QSqlQuery &query, const QString &field, const QVariant &value) const
{
    auto type = IMetaUtil::typeId(value);
    if(static_cast<int>(type) >= QMetaType::User && (value.typeName() == std::string("std::string") || value.typeName() == std::string("IString"))){
        return query.bindValue(field, value.value<QString>());
    }

    switch(type){
    case QMetaType::QDate:
    case QMetaType::QTime:
    case QMetaType::QDateTime:
        query.bindValue(field, value.toString());
        break;
    default:
        query.bindValue(field, value);
    }
}

QString IRdbSqlServerDialect::quoteName(const QString &name) const
{
    return "[" + name + "]";
}

$PackageWebCoreEnd
