#pragma once

#include "core/util/IHeaderUtil.h"
#include "core/unit/ISoloUnit.h"

$PackageWebCoreBegin

class ICmdAction;
class ICmdWare;
class ICmdRequest;
class ICmdManage : public ISoloUnit<ICmdManage>
{
public:
    ICmdManage() = default;

public:
    void printHelp();

public:
    void registAction(ICmdAction*);
    ICmdAction* getAction(const ICmdRequest& request);

private:
    QList<ICmdAction*> m_actions;
};

$PackageWebCoreEnd
