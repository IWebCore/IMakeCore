#pragma once

#include "rdb/entity/IRdbValueGeneratorInterface.h"
using namespace IWebCore;

class IRdbUuidValueGenerator : public IRdbValueGeneratorInterface<IRdbUuidValueGenerator>
{
public:
    IRdbUuidValueGenerator() = default;

public:
    virtual QString name() const final;
    virtual QVariant generator() const final;
};

