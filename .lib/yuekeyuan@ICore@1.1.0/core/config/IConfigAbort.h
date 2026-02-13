#pragma once

#include "core/abort/IAbortInterface.h"

$PackageWebCoreBegin

class IConfigAbort : public IAbortInterface<IConfigAbort>
{
    $AsAbort(
        ConfigurationResolveJsonError,
        ConfigurationResolveTomlError,
        ConvertToStringTypeError,
        ConvertTypeNotImplimented
    )
protected:
    virtual QMap<int, QString> abortDescription() const final{
        return {
            {ConfigurationResolveJsonError, "error when parse json files"},
            {ConfigurationResolveTomlError, "error when parse toml files"},
            {ConvertToStringTypeError, "json value can not be converted to string type"},
            {ConvertTypeNotImplimented, "this kind if type is not implimented"}
        };
    }
};

$PackageWebCoreEnd
