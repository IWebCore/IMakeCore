#include "IRdbUuidValueGenerator.h"

QString IRdbUuidValueGenerator::name() const
{
    return "uuid";
}

QVariant IRdbUuidValueGenerator::generator() const
{
    return QUuid::createUuid().toString();
}
