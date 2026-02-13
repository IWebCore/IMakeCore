#pragma once

#include "core/util/IPreProcessorUtil.h"

$PackageWebCoreBegin

struct INoCopyMoveUnit
{
public:
    INoCopyMoveUnit() =default;
    ~INoCopyMoveUnit() = default;

    INoCopyMoveUnit(const INoCopyMoveUnit&) = delete;
    INoCopyMoveUnit& operator=(const INoCopyMoveUnit&) = delete;
    INoCopyMoveUnit(INoCopyMoveUnit&&) = delete;
    INoCopyMoveUnit& operator=(INoCopyMoveUnit&&) = delete;
};

$PackageWebCoreEnd
