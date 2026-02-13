#include "IRdbManage.h"

#include "rdb/IRdbAbort.h"

$PackageWebCoreBegin

void IRdbManage::regiterAutoGenerateKeyFunction(const QString &type, IRdbManage::GeneratorFunction fun)
{
    if(m_valueGeneratorMap.contains(type)){
        QString tip = "key name : " + type;
        IRdbAbort::abortDuplicatedKey(tip, $ISourceLocation);
    }
    m_valueGeneratorMap[type] = fun;
}

IRdbManage::GeneratorFunction IRdbManage::getAutoGenerateKeyFunction(const QString &type)
{
    if(m_valueGeneratorMap.contains(type)){
        return m_valueGeneratorMap[type];
    }
    return nullptr;
}

$PackageWebCoreEnd
