#include "ITaskCatagory.h"
#include "core/task/ITaskWare.h"
#include "core/config/IContextImport.h"

$PackageWebCoreBegin

bool ITaskCatagory::$isCatagoryDefaultEnabled() const
{
    return true;
}

const std::string& ITaskCatagory::$name() const
{
    return $catagory();
}

bool ITaskCatagory::isCatagoryEnabled() const
{
    QString name = QString::fromStdString($name()).split("::").last();
    auto pathEnabled = std::string("/CATAGORY_ENABLE_STATE/") + name.toStdString();
    $ContextBool value{pathEnabled, $isCatagoryDefaultEnabled()};
    return *value;
}

void ITaskCatagory::addTask(ITaskWare *ware)
{
    m_taskWares.append(ware);
}

void ITaskCatagory::sortTask()
{
    IOrderUnitUtil::sortUnit(m_taskWares);
}

void ITaskCatagory::execTaskNodes() const
{
    for(auto& node : m_taskWares){
        if(!node->isTaskEnabled()){
            continue;
        }
        node->$task();
    }
}

void ITaskCatagory::printTaskInfo() const
{
    static $ContextBool value{"/task/taskOutputEnabled", false};
    if(!*value){
        return;
    }

    qDebug().noquote().nospace() << "[+] " << QString::number($order()).leftJustified(4, ' ') << QString::fromStdString($name());
    for(const auto& node : m_taskWares){
        if(node->isTaskEnabled()){
            qDebug().noquote().nospace() << QStringLiteral("    [√] ")
                               << QString::number(node->$order()).leftJustified(4, ' ')
                               << QString::fromStdString(node->$name());
        }
    }
    qDebug() << "\n";
}

$PackageWebCoreEnd
