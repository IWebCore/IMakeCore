#include "IProfileLoadJsonTask.h"
#include "core/util/IFileUtil.h"
#include "core/config/IProfileManage.h"
#include "core/config/IContextImport.h"
#include "core/config/IConfigAbort.h"
#include "core/abort/IAbortInterface.h"

$PackageWebCoreBegin

namespace detail
{
    IJson parseJsonFile(const QString& path);
}

IProfileLoadJsonTask::IProfileLoadJsonTask()
{
}

double IProfileLoadJsonTask::$order() const
{
    return 99.0;
}

IJson IProfileLoadJsonTask::config()
{
    auto paths = getFilteredPaths();
    for(auto path : paths){
        auto obj = detail::parseJsonFile(path);
        IProfileManage::instance().addConfig(obj);
    }

    return {};
}

QStringList IProfileLoadJsonTask::nameFilters() const
{
    return {"*.json"};
}

void IProfileLoadJsonTask::$task()
{
    $ContextBool enableConfigFiles{"/config/enableConfigFiles", false};
    if(*enableConfigFiles){
        auto value = config();
        if(!value.is_null()){
            IProfileManage::instance().addConfig(value);
        }
    }
}

IJson detail::parseJsonFile(const QString &path)
{
    bool ok;
    QString content = IFileUtil::readFileAsString(path, ok);
    if(ok){
        auto stdStringContent = content.toStdString();
        if(IJson::accept(stdStringContent)){
            return IJson::parse(stdStringContent);
        }
    }

    IConfigAbort::abortConfigurationResolveJsonError("path at:" + path, $ISourceLocation);
    return nullptr;
}

$PackageWebCoreEnd
