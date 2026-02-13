#include "ICmdRequest.h"

$PackageWebCoreBegin

ICmdRequest::ICmdRequest(const QStringList &cmds)
    : m_cmds(cmds)
{
    parseCmd();
}

void ICmdRequest::parseCmd()
{
    m_executable = m_cmds[0];
    parsePaths();
    parseAguments();
    parseOptions();
    parseHelp();
}

void ICmdRequest::parsePaths()
{
    for(int i=1; i<m_cmds.length(); i++){
        QString cmd = m_cmds[i];
        if(!cmd.startsWith("-")){
            m_paths.append(cmd);
        }else{
            break;
        }
    }
}

void ICmdRequest::parseAguments()
{
    bool flag{false};
    for(int i=1; i<m_cmds.length(); i++){
        const QString& cmd = m_cmds[i];
        if(flag){
            if(!cmd.startsWith("-")){
                m_arguments.push_back(cmd);
                continue;
            }else {
                flag = false;
            }
        }
        if(cmd == "--"){
            flag = true;
        }
    }
}

void ICmdRequest::parseOptions()
{
    QString option;
    for(int i=1; i<m_cmds.length(); i++){
        const QString& cmd = m_cmds[i];
        if(!option.isEmpty()){
            if(!cmd.startsWith("-")){
                m_options[option].append(cmd);
                continue;
            }else{
                option = "";
            }
        }
        if(cmd != "--" && cmd.startsWith("-")){
            option = cmd;
            m_options[option] = QStringList{};
        }
    }
}

void ICmdRequest::parseHelp()
{
    for(int i=1; i<m_cmds.length(); i++){
        const QString& cmd = m_cmds[i];
        if(cmd == "-?"){
            m_isHelp = true;
            return;
        }
    }
}

$PackageWebCoreEnd
