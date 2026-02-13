#pragma once

#include "core/util/IHeaderUtil.h"
#include "core/task/unit/ITaskWareUnit.h"
#include "core/unit/ISoloUnit.h"
#include "cmd/ICmdManage.h"
#include "cmd/ICmdCatagory.h"
#include "cmd/ICmdWare.h"
#include "cmd/ICmdException.h"
#include "cmd/pp/IAsCmdPreProcessor.h"
#include "cmd/pp/ICmdMappingPreProcessor.h"
#include "cmd/pp/ICmdOptionValuePreProcessor.h"
#include "cmd/pp/ICmdOptionPreProcessor.h"
#include "cmd/pp/ICmdArgXPreProcessor.h"
#include "cmd/pp/ICmdArgsPreProcessor.h"
#include "cmd/pp/ICmdArg1PreProcessor.h"
#include "cmd/pp/ICmdArg2PreProcessor.h"
#include "cmd/pp/ICmdArg3PreProcessor.h"
#include "cmd/pp/ICmdArg4PreProcessor.h"
#include "cmd/pp/ICmdArg5PreProcessor.h"
#include "cmd/pp/ICmdArg6PreProcessor.h"
#include "cmd/pp/ICmdArg7PreProcessor.h"
#include "cmd/pp/ICmdArg8PreProcessor.h"
#include "cmd/pp/ICmdArg9PreProcessor.h"

$PackageWebCoreBegin

namespace detail
{
    template<typename T>
    void setValue(T& value, const QStringList& raws);
}

template<typename T, bool enabled=true>
class ICmdInterface : public ICmdWare, public ITaskWareUnit<T, ICmdCatagory, enabled>, public ISoloUnit<T>
{
public:
    ICmdInterface() = default;

public:
    virtual void $task() final;
};

template<typename T, bool enabled>
void ICmdInterface<T, enabled>::$task()
{
    QString name = T::staticMetaObject.className();
    auto clsInfos = IMetaUtil::getMetaClassInfoMap(T::staticMetaObject);
    auto methods = IMetaUtil::getMetaMethods(T::staticMetaObject);
    auto props = IMetaUtil::getMetaProperties(T::staticMetaObject);
    parseAction(this, name, clsInfos, methods, props);
}

$PackageWebCoreEnd
