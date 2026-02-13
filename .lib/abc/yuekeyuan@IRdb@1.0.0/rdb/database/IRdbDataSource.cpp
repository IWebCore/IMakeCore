#include "IRdbDataSource.h"
#include "core/config/IProfileImport.h"
#include "rdb/IRdbAbort.h"

$PackageWebCoreBegin

template class IBeanInterface<IRdbDataSource>;

IRdbDataSource::IRdbDataSource()
{
}

IRdbDataSource IRdbDataSource::fromConfig(const std::string & path)
{
    $IJson json{path};
    if(json.isLoadedValue()){
        if(auto source = IRdbDataSource::fromJson(*json)){
            return *source;
        }
    }
    QString cause = QString::fromStdString(path) + " are not a valid json config path";
    IRdbAbort::abortDataSourceError(cause, $ISourceLocation);
    return {};
}

$PackageWebCoreEnd
