#include "ITaskWare.h"
#include "core/config/IContextImport.h"

$PackageWebCoreBegin

bool ITaskWare::$isTaskDefaultEnabled() const
{
    return true;
}

bool ITaskWare::isTaskEnabled() const
{
    QString name = QString::fromStdString($name()).split("::").last();
    auto path = std::string("/TASK_ENABLE_STATE/")+ $catagory() + "/" + name.toStdString();
    $ContextBool value{path, this->$isTaskDefaultEnabled()};
    return *value;
}

$PackageWebCoreEnd
