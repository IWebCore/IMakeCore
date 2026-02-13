#pragma once

#include "core/util/IPreProcessorUtil.h"
#include "rdb/pp/IRdbPreProcessor.h"

#define $AsTable(klassName) \
    Q_CLASSINFO("sql_entityName", #klassName)

#define $SqlType(name, type)  \
    Q_CLASSINFO(PP_STRING(sql_field_type__##name), #type)

#define $PrimaryKey(name) \
    Q_CLASSINFO(PP_STRING(sql_primaryKey__##name), #name)

#define $NotNull(name)  \
    Q_CLASSINFO(PP_STRING(sql_not_null_key__##name), #name)

#define $Unique(name) \
    Q_CLASSINFO(PP_STRING(sql_unique_key__##name), #name)

#define $AutoIncrement(name)    \
    Q_CLASSINFO(PP_STRING(sql_auto_increment__##name), #name)

#define $Constraint(name, value) \
    Q_CLASSINFO(PP_STRING(sql_column_constraint__##name), value)

#define $GenerateValue(name, value) \
    Q_CLASSINFO(PP_STRING(sql_generate_value__##name), #value)

#define $SqlIgnored(name)   \
    Q_CLASSINFO(PP_STRING(sql_ignored_key__##name), #name)

#define $TableField $Column
#define $TableFieldDeclare $ColumnDeclare
