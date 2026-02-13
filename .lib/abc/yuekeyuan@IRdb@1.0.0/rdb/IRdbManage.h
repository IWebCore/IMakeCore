#pragma once

#include "core/util/IPreProcessorUtil.h"
#include "core/unit/ISoloUnit.h"

#if ! __has_include(<QtSql>)
    #error "IRdb package need Qt sql module support"
#endif

$PackageWebCoreBegin

class IRdbManage : public ISoloUnit<IRdbManage>
{
public:
    using GeneratorFunction = std::function<QVariant()>;
    using QueryLogFunction  = std::function<void(const QSqlQuery&)>;

public:
    IRdbManage() = default;

public:
    void regiterAutoGenerateKeyFunction(const QString& type, GeneratorFunction);
    GeneratorFunction getAutoGenerateKeyFunction(const QString& type);

private:
    QMap<QString, GeneratorFunction> m_valueGeneratorMap;
};

$PackageWebCoreEnd
