#pragma once

#include "core/util/IHeaderUtil.h"

$PackageWebCoreBegin

class ICmdRequest
{
public:
    ICmdRequest() = default;
    ICmdRequest(const QStringList& cmds);

private:
    void parseCmd();
    void parsePaths();
    void parseAguments();
    void parseOptions();
    void parseHelp();

public:
    bool m_isHelp{false};
    QStringList m_cmds;
    QString m_executable;
    QStringList m_paths;
    QStringList m_arguments;
    QMap<QString, QStringList> m_options;
};

$PackageWebCoreEnd
