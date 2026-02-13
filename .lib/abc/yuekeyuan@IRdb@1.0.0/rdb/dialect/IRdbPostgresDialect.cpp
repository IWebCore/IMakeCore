#include "IRdbPostgresDialect.h"
#include "rdb/IRdbAbort.h"
#include "rdb/entity/IRdbTableInfo.h"

QString IRdbPostgresDialect::databaseType() const
{
    return "Postgres";
}

QString IRdbPostgresDialect::getSqlType(const IRdbTableInfo &info, int index) const
{
    static const QMap<int, QString> map = {
        {QMetaType::Char, "smallint"},
        {QMetaType::UChar, "smallint"},
        {QMetaType::Short, "smallint"},
        {QMetaType::UShort, "integer"},
        {QMetaType::Int, "integer"},
        {QMetaType::UInt, "integer"},
        {QMetaType::Long, "bigint"},
        {QMetaType::ULong, "bigint"},
        {QMetaType::LongLong, "bigint"},
        {QMetaType::ULongLong, "bigint"},
        {QMetaType::Double, "double precision"},
        {QMetaType::Float, "real"},
        {QMetaType::Bool, "boolean"},
        {QMetaType::QDate, "date"},
        {QMetaType::QTime, "time"},
        {QMetaType::QDateTime, "timestamp"},
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

QString IRdbPostgresDialect::createSqlCommonKeyClause(const IRdbTableInfo &info, int index) const
{
    const auto& name = info.m_fieldNames[index];

    QString piece = name;
    if(info.m_autoIncrement == index){
        QList<QMetaType::Type> types = {
            QMetaType::Long, QMetaType::LongLong, QMetaType::ULong, QMetaType::ULongLong
        };
        if(types.contains(info.m_fields[index].m_typeId)){
            piece = piece + " BIGSERIAL";
        }else{
            piece = piece + " SERIAL";
        }
    }else{
        auto sqlType = getSqlType(info, index);
        piece = piece + " " + sqlType;
    }

    if(info.m_notNullKeys.contains(index)){
        piece.append(" NOT NULL");
    }
    if(info.m_uniqueKeys.contains(index)){
        piece.append(" UNIQUE");
    }
    if(info.m_primaryKey == index){
        piece.append(" PRIMARY KEY");
    }
    if(info.m_constraints.contains(index)){
        piece.append(" ").append(info.m_constraints[index]);
    }
    return piece;
}
