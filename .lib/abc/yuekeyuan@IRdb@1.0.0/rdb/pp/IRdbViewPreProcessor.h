#pragma once

#include "rdb/pp/IRdbPreProcessor.h"

#define $AsView(viewName)   \
    Q_CLASSINFO("sql_entityName", #viewName)

#define $CreateViewSql( sql )       \
    Q_CLASSINFO("sql_createViewSql", sql)

#define $ViewField $Column
#define $ViewFieldDeclare $ColumnDeclare
