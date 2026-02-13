#pragma once

#include "core/abort/IAbortInterface.h"

$PackageWebCoreBegin

class IBeanAbort : public IAbortInterface<IBeanAbort>
{
    $AsAbort(
        InvalidFieldType,
        ToJsonMethodNotExist,
        LoadJsonMethodNotExist,
        JsonValidatorSignatureInvalid,
        TypeNotRegisteredForJsonConvertion
    )
protected:
    virtual QMap<int, QString> abortDescription() const final{
        return {
            {InvalidFieldType, "this field type is not supported"},
            {ToJsonMethodNotExist, "toJson method of one field not exist, please check it"},
            {LoadJsonMethodNotExist, "loadJson method of one field not exist, please check it"},
            {JsonValidatorSignatureInvalid, "json validator function signature shoud be 'bool funName(const IJson&) const'"},
            {TypeNotRegisteredForJsonConvertion, "this typeId is not register fromJson / toJson function to manage, please check it"},
        };
    }
};

$PackageWebCoreEnd
