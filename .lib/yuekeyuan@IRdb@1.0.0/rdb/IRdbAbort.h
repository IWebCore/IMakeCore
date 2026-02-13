#pragma once

#include "core/abort/IAbortInterface.h"

#if ! __has_include(<QtSql>)
    #error "IRdb package need Qt sql module support"
#endif

$PackageWebCoreBegin

class IRdbAbort : public IAbortInterface<IRdbAbort>
{
    $AsAbort(
        where_sql_start_with_OR,
        EntityCannotBeCreated,
        DialectError,
        TableDeclarationError,

        RdbUtilError,

        DataSourceError,
        ConnectionTraitError,

        DuplicatedKey
    )
protected:
    virtual QMap<int, QString> abortDescription() const final{
        return {
            {where_sql_start_with_OR, "your where sql start with OR, please check your code"},
            {EntityCannotBeCreated, "your used table/view cannot be created when start program, please check"},
            {DialectError, "dialect exist error"},
            {TableDeclarationError, "table declaration not correct, please check your table declaration"},
            {RdbUtilError, "error exist in your rdbutil, please check it"},
            {DataSourceError, "DataSource you configured not correct, please check it"},
            {ConnectionTraitError, "Connection Trait configured not correct, please check it"},
            {DuplicatedKey, "duplicated key exist"}
        };
    }
};

$PackageWebCoreEnd
