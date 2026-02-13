#pragma once

#include "core/util/IHeaderUtil.h"
#include "INodyResolverInterface.h"

$PackageWebCoreBegin

struct INody;
class INodyDefaultResolver : public INodyResolverInterface<INodyDefaultResolver>
{
public:
    INodyDefaultResolver();

public:
    virtual bool match(const IString& path) final;
    virtual std::string parse(const IString& path, const IJson& json) final;

public:
    virtual bool isValid() const;
    virtual void $task() final;

private:
    void prepareNodies();

    QStringList findFiles(const QString& basePath, const QStringList& pattern);

private:
    QMap<IString, INody*> m_nodies;
};

$PackageWebCoreEnd
