#pragma once

#include "core/abort/IAbortInterface.h"

$PackageWebCoreBegin

class ITcpAbort : public IAbortInterface<ITcpAbort>
{
    $AsAbort(
        ResolverFactoryNotRegistered
    )
public:
    virtual QMap<int, QString> abortDescription() const final
    {
        return {
            {ResolverFactoryNotRegistered, "communication resolver factory not registered, please check it."}
        };
    }
};

$PackageWebCoreEnd
