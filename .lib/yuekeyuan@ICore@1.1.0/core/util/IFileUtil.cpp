#include "IFileUtil.h"

$PackageWebCoreBegin

QString IFileUtil::readFileAsString(const QString &path, bool& ok)
{
    return readFileAsByteArray(path, &ok);
}

IResult<QString> IFileUtil::readFileAsString(const QString &path)
{
    bool ok;
    auto content = readFileAsString(path, ok);
    if(ok){
        return content;
    }
    return std::nullopt;
}

QString IFileUtil::readFileAsString2(const QString &path)
{
     bool ok;
     QString content = readFileAsString(path, ok);
     if(!ok){
         return {};
     }
     return content;
}

QByteArray IFileUtil::readFileAsByteArray(const QString &path, bool* ok)
{
    QFile file(path);
    if(!file.exists() || !file.open(QFile::ReadOnly)){
        if(ok){
            *ok = false;
        }
        return {};
    }

    QByteArray content = file.readAll();
    file.close();
    if(ok){
        *ok = true;
    }
    return content;
}

QStringList IFileUtil::readFileAsStringList(const QString &path)
{
    QStringList lines;

    QFile file(path);
    if (!file.open(QIODevice::ReadOnly | QIODevice::Text)) {
        qWarning("Error: Failed to open file %s", qUtf8Printable(path));
        return lines;
    }

    QTextStream in(&file);
    while (!in.atEnd()) {
        QString line = in.readLine().trimmed();
        if (!line.isEmpty()) {
            lines.append(line);
        }
    }

    file.close();
    return lines;
}



void IFileUtil::writeToFile(const QString &path, const QString &content)
{
    QFileInfo fileInfo(path);
    QDir dir = fileInfo.absoluteDir();
    if (!dir.exists()) {
        if (!dir.mkpath(".")) {
            qWarning() << "Failed to create directory:" << dir.path();
            return;
        }
    }

    QFile file(path);
    if (!file.open(QIODevice::WriteOnly | QIODevice::Text)) {
        qWarning() << "Failed to open file:" << path;
        return;
    }

    QTextStream out(&file);
    out << content;
}

void IFileUtil::writeToFile(const QString &path, const QByteArray &content)
{
    QFileInfo fileInfo(path);
    QDir dir = fileInfo.absoluteDir();
    if (!dir.exists()) {
        if (!dir.mkpath(".")) {
            qWarning() << "Failed to create directory:" << dir.path();
            return;
        }
    }

    QFile file(path);
    if (!file.open(QIODevice::WriteOnly)) {
        qWarning() << "Failed to open file:" << path;
        return;
    }
    file.write(content);
    file.close();
}

$PackageWebCoreEnd
