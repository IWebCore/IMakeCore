#include "INodyDefaultResolver.h"
#include "core/config/IProfileImport.h"
#include "core/util/IFileUtil.h"
#include "INody.h"
#include "INodyParser.h"
#include "INodyManage.h"

INodyDefaultResolver::INodyDefaultResolver()
{
}

bool INodyDefaultResolver::match(const IString& path)
{
    return m_nodies.contains(path);
}

std::string INodyDefaultResolver::parse(const IString& path, const IJson &json)
{
    if(m_nodies.contains(path)){
        return m_nodies[path]->execute(json, {});
    }
    return {};
}

bool INodyDefaultResolver::isValid() const
{
    static $Bool enabled("/http/nody/enabled", true);
    if(!enabled.value()){
        return false;
    }

    static $QString path("/http/nody/path");
    if(path.value().isEmpty()){
        return false;
    }

    return true;
}

void INodyDefaultResolver::$task()
{
    if(isValid()){
        prepareNodies();
        INodyManage::instance().registNodyResolverWare(this);
    }
}

void INodyDefaultResolver::prepareNodies()
{
    $QString path("/http/nody/path");
    auto fileNames = findFiles(*path, {"*.yky"});

    INodyParser parser(*path);
    for(const QString& fileName : fileNames){
        auto nody = parser.parseFile(fileName);
        if(nody){
            m_nodies[IString(fileName.toStdString())] = nody;
        }
    }
}

QStringList INodyDefaultResolver::findFiles(const QString &basePath, const QStringList &pattern)
{
    QStringList results;
    QString canonicalPath = QDir(basePath).canonicalPath();
    if (canonicalPath.isEmpty()) {
        qWarning() << "Invalid directory path:" << basePath;
        return results;
    }
    QDirIterator it(basePath, pattern, QDir::Files,  QDirIterator::Subdirectories);

    while (it.hasNext()) {
        QString absPath = it.next();
        QString relativePath = QDir(canonicalPath).relativeFilePath(absPath);
        results.append(relativePath);
    }
    return results;
}

