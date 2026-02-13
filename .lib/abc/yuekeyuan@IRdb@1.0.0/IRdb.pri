INCLUDEPATH += $$PWD

HEADERS += \
    $$PWD/rdb/IRdbAbort.h \
    $$PWD/rdb/IRdbAnnomacro.h \
    $$PWD/rdb/IRdbCatagory.h \
    $$PWD/rdb/IRdbManage.h \
    $$PWD/rdb/IRdbUtil.h \
    $$PWD/rdb/ISqlQuery.h \
    $$PWD/rdb/clause/IRdbClause.h \
    $$PWD/rdb/clause/IRdbCondition.h \
    $$PWD/rdb/clause/IRdbGroupByClause.h \
    $$PWD/rdb/clause/IRdbHavingClause.h \
    $$PWD/rdb/clause/IRdbLimitClause.h \
    $$PWD/rdb/clause/IRdbOrderByClause.h \
    $$PWD/rdb/clause/IRdbWhereClause.h \
    $$PWD/rdb/clause/impl/IRdbConditionImpl.h \
    $$PWD/rdb/database/IRdbConnection.h \
    $$PWD/rdb/database/IRdbConnectionTrait.h \
    $$PWD/rdb/database/IRdbDataSource.h \
    $$PWD/rdb/database/IRdbDatabaseInterface.h \
    $$PWD/rdb/database/IRdbDatabaseWare.h \
    $$PWD/rdb/database/IRdbMariaDbDatabaseInterface.h \
    $$PWD/rdb/database/IRdbMySqlDatabaseInterface.h \
    $$PWD/rdb/database/IRdbPostgresDatabaseInterface.h \
    $$PWD/rdb/database/IRdbSqlServerDatabaseInterface.h \
    $$PWD/rdb/database/IRdbSqliteDatabaseInterface.h \
    $$PWD/rdb/dialect/IRdbDialectInterface.h \
    $$PWD/rdb/dialect/IRdbDialectWare.h \
    $$PWD/rdb/dialect/IRdbMariaDbDialect.h \
    $$PWD/rdb/dialect/IRdbMysqlDialect.h \
    $$PWD/rdb/dialect/IRdbPostgresDialect.h \
    $$PWD/rdb/dialect/IRdbSqlServerDialect.h \
    $$PWD/rdb/dialect/IRdbSqliteDialect.h \
    $$PWD/rdb/entity/IRdbEntityInfo.h \
    $$PWD/rdb/entity/IRdbTableInfo.h \
    $$PWD/rdb/entity/IRdbTableInterface.h \
    $$PWD/rdb/entity/IRdbTableInterface_flatten.h \
    $$PWD/rdb/entity/IRdbValueGeneratorInterface.h \
    $$PWD/rdb/entity/IRdbViewInfo.h \
    $$PWD/rdb/entity/IRdbViewInterface.h \
    $$PWD/rdb/entity/IRdbViewInterface_flatten.h \
    $$PWD/rdb/exception/IRdbException.h \
    $$PWD/rdb/impl/IRdbUuidValueGenerator.h \
    $$PWD/rdb/model/IRdbEntityModelWare.h \
    $$PWD/rdb/model/IRdbTableModelInterface.h \
    $$PWD/rdb/model/IRdbTableModelInterface_flatten.h \
    $$PWD/rdb/model/IRdbViewModelInterface.h \
    $$PWD/rdb/model/IRdbViewModelInterface_flatten.h \
    $$PWD/rdb/pp/IRdbPreProcessor.h \
    $$PWD/rdb/pp/IRdbTablePreProcessor.h \
    $$PWD/rdb/pp/IRdbViewPreProcessor.h

SOURCES += \
    $$PWD/rdb/IRdbCatagory.cpp \
    $$PWD/rdb/IRdbManage.cpp \
    $$PWD/rdb/IRdbUtil.cpp \
    $$PWD/rdb/ISqlQuery.cpp \
    $$PWD/rdb/clause/IRdbCondition.cpp \
    $$PWD/rdb/clause/IRdbGroupByClause.cpp \
    $$PWD/rdb/clause/IRdbHavingClause.cpp \
    $$PWD/rdb/clause/IRdbLimitClause.cpp \
    $$PWD/rdb/clause/IRdbOrderByClause.cpp \
    $$PWD/rdb/clause/IRdbWhereClause.cpp \
    $$PWD/rdb/database/IRdbConnection.cpp \
    $$PWD/rdb/database/IRdbConnectionTrait.cpp \
    $$PWD/rdb/database/IRdbDataSource.cpp \
    $$PWD/rdb/database/IRdbDatabaseWare.cpp \
    $$PWD/rdb/dialect/IRdbDialectWare.cpp \
    $$PWD/rdb/dialect/IRdbMariaDbDialect.cpp \
    $$PWD/rdb/dialect/IRdbMysqlDialect.cpp \
    $$PWD/rdb/dialect/IRdbPostgresDialect.cpp \
    $$PWD/rdb/dialect/IRdbSqlServerDialect.cpp \
    $$PWD/rdb/dialect/IRdbSqliteDialect.cpp \
    $$PWD/rdb/entity/IRdbEntityInfo.cpp \
    $$PWD/rdb/entity/IRdbTableInfo.cpp \
    $$PWD/rdb/entity/IRdbViewInfo.cpp \
    $$PWD/rdb/impl/IRdbUuidValueGenerator.cpp
