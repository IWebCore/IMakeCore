#include "ISoloUnit.h"
#include "core/abort/IGlobalAbort.h"

$PackageWebCoreBegin

void ISoloUnitDetail::abortError(QString content)
{
    IGlobalAbort::abortSingletonInstanceCreateError(content);
}

$PackageWebCoreEnd
