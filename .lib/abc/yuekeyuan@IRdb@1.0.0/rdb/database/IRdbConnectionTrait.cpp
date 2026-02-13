#include "IRdbConnectionTrait.h"
#include "core/config/IProfileImport.h"
#include "rdb/IRdbAbort.h"

$PackageWebCoreBegin

template class IBeanInterface<IRdbConnectionTrait>;

IRdbConnectionTrait IRdbConnectionTrait::fromConfig(const std::string &path)
{
    $IJson json(path);
    if(json.isLoadedValue()){
        IRdbConnectionTrait trait;
        if(auto trait = IRdbConnectionTrait::fromJson(*json)){
            return *trait;
        }
    }

    QString cause = "please check your connection trait path: " + QString::fromStdString(path);
    IRdbAbort::abortConnectionTraitError(cause, $ISourceLocation);
    return {};
}

$PackageWebCoreEnd
