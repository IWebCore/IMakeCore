#include "IContextLoadSystemVariableTask.h"

$PackageWebCoreBegin

namespace detail
{
    IJson getSystemEnvironment();
}

IContextLoadSystemVariableTask::IContextLoadSystemVariableTask()
{
}

IJson IContextLoadSystemVariableTask::config()
{
    return detail::getSystemEnvironment();
}

IJson detail::getSystemEnvironment(){
    IJson obj = IJson::object();
    QStringList environment = QProcess::systemEnvironment();
    for(auto str : environment)
    {
        auto index = str.indexOf('=');
        auto key = str.left(index);
        auto value = str.mid(index +1 );
        obj[key.toStdString()] = value.toStdString();
    }
    return obj;
}

$PackageWebCoreEnd
