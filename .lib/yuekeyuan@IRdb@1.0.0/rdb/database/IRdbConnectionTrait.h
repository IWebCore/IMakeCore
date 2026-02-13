#pragma once

#include "core/bean/IBeanInterface.h"

$PackageWebCoreBegin

class IRdbConnectionTrait : public IBeanInterface<IRdbConnectionTrait>
{
    Q_GADGET
public:
    IRdbConnectionTrait() = default;
    static IRdbConnectionTrait fromConfig(const std::string&);

public:
    $BeanField(int, maxConnection, 50)

    $BeanField(int, minConnection, 1)

    $BeanField(int, connectionTimeout, 30) // 30s

    $BeanField(int, timerDuration, 300) // 6min

    $BeanField(int, idleTimeout, 600) // 12min
};

extern template class IBeanInterface<IRdbConnectionTrait>;

$PackageWebCoreEnd
