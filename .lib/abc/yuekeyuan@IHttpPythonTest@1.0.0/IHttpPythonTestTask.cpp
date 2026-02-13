#include "IHttpPythonTestTask.h"
#include "core/config/IContextImport.h"
#include "core/config/IProfileImport.h"
#include "core/application/iApp.h"
#include "core/abort/IAbortInterface.h"

$IPackageBegin(IPubCore, IHttpPythonTest)

class IHttpPythonTestAbort : public IAbortInterface<IHttpPythonTestAbort>
{
    $AsAbort(
        ExecuteCommandError,
        PythonLibNotInstalled
    )

protected:
    virtual QMap<int, QString> abortDescription() const
    {
        return {
            {ExecuteCommandError, "error occured when execute command"},
            {PythonLibNotInstalled, "please install pytest lib"}
        };
    }
};

void IHttpPythonTestTask::$task()
{
    $ContextBool contextEnabled{"/test/pytest/enabled", false};
    if(!(*contextEnabled)){
        return;
    }

    std::thread thread([&](){
        checkPytestExist();
        m_scriptDir = getScriptDir();
        qDebug() << m_scriptDir;
        if(m_scriptDir.isEmpty()){
            qDebug() << "IHttpPythonTestTask: script dir not exist";
            return;
        }
        writeConfig();
        startTest();
    });
    thread.detach();
}

void IHttpPythonTestTask::checkPytestExist()
{
    QString pythonCmd = "python";

    QProcess checkPython;
    checkPython.start("python3", QStringList() << "--version");
    checkPython.waitForFinished();
    if (checkPython.exitCode() == 0) {
        pythonCmd = "python3";
    }

    QProcess process;
    process.start(pythonCmd, QStringList() << "-m" << "pytest" << "--version");
    if (!process.waitForFinished()) {
        qDebug() << process.arguments() << pythonCmd;
        QString tip = "Error executing command:" + process.errorString();
        IHttpPythonTestAbort::abortExecuteCommandError(tip, $ISourceLocation);
    }

    QByteArray result = process.readAllStandardOutput();
    if (!result.isEmpty()) {
        return;
    }

    QByteArray error = process.readAllStandardError();
    if (!error.isEmpty()) {
        QString tip =  "Error:" + error;
        IHttpPythonTestAbort::abortExecuteCommandError(tip, $ISourceLocation);
    } else {
        IHttpPythonTestAbort::abortPythonLibNotInstalled($ISourceLocation);
    }
}

QString IHttpPythonTestTask::getScriptDir()
{
    QVector<decltype(&IHttpPythonTestTask::getContextScriptDir)> funs{
        &IHttpPythonTestTask::getApplicationScriptDir,
        &IHttpPythonTestTask::getContextScriptDir,
        &IHttpPythonTestTask::getSourceRootScriptDir
    };

    for(auto fun : funs){
        QString value = std::invoke(fun, this);
        if(!value.isEmpty()){
            return value;
        }
    }
    return {};
}

QString IHttpPythonTestTask::getContextScriptDir()
{
    $ContextQString contextPath{"/test/pytest/scriptDir"};
    if(contextPath.isLoadedValue()){
        if(QDir(*contextPath).exists()){
            return *contextPath;
        }
    }

    $ProfileQString profilePath("/test/pytest/scriptDir");
    if(profilePath.isLoadedValue()){
        if(QDir(*profilePath).exists()){
            return *profilePath;
        }
    }

    return {};
}

QString IHttpPythonTestTask::getApplicationScriptDir()
{
    auto parentPath = iApp->applicationPath();
    auto path =  parentPath+ "/pytest";
    if(QDir(path).exists()){
        return path;
    }
    path = parentPath + "/test/pytest";
    if(QDir(path).exists()){
        return path;
    }
    return {};
}

QString IHttpPythonTestTask::getSourceRootScriptDir()
{
#ifdef IWEBCORE_PROJECT_DIR
    auto path = QString(IWEBCORE_PROJECT_DIR) + "/pytest";
    if(QDir(path).exists()){
        return path;
    }

    path = QString(IWEBCORE_PROJECT_DIR) + "/test/pytest";
    if(QDir(path).exists()){
        return path;
    }
#endif
    return {};
}

void IHttpPythonTestTask::startTest()
{   
    qDebug() << "start to run pytest";
    qDebug() << "path at" << m_scriptDir;
    QProcess* process = new QProcess();
    process->setWorkingDirectory(m_scriptDir);

    QStringList arguments;
#if defined(_WIN32) || defined(WIN32)
    arguments << "--html=report.html"
              << "--self-contained-html";
#endif

    process->start("pytest", arguments);
    process->waitForFinished();

    qDebug().noquote() << process->readAllStandardOutput();
    qDebug().noquote() << process->readAllStandardError();
    delete process;

#if defined(_WIN32) || defined(WIN32)
    openTest();
#endif
}

void IHttpPythonTestTask::openTest()
{
    QProcess* process = new QProcess();
    process->setWorkingDirectory(m_scriptDir);
    process->start("cmd", QStringList{"/c", "start", "report.html"});
    process->waitForFinished();
    delete process;
}

void IHttpPythonTestTask::writeConfig()
{
    auto path = m_scriptDir + "/ServerConfig.py";
    QFile file(path);
    if(file.open(QFile::WriteOnly)){
        QTextStream stream(&file);

        $ContextQString ip{"/runtime/tcp/ip", "127.0.0.1"};
        $ContextInt port{"/runtime/tcp/port", 8550};
        $ContextBool isSsl{"/runtime/tcp/ssl", false};
        stream << "port=\"" << *port << "\"\n";
        stream << "ip=\"" << *ip << "\"\n";
        stream << "isSsl=" << (*isSsl ? "True" : "False") << "\n";
        if(*isSsl){
            stream << "serverAddress=\"https://" << *ip << ":" << *port << "\"\n";
        }else{
            stream << "serverAddress=\"http://" << *ip << ":" << *port << "\"\n";
        }

        file.close();
    }
}

$IPackageEnd(IPubCore, IHttpPythonTest)
