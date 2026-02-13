#include "ILoadProfileFileUnit.h"
#include "core/config/IContextImport.h"
#include <QRegularExpression>

$PackageWebCoreBegin

namespace detail
{
    QStringList getConfigDirs();
}

QStringList ILoadProfileFileUnit::getFilteredPaths() const
{
    QStringList filesPaths;
    auto dirs = detail::getConfigDirs();
    for(auto dirPath : dirs){
        QDir dir(dirPath);
        auto entries = dir.entryInfoList(nameFilters());
        for(const auto& fileInfo : entries){
            if(fileInfo.isFile()){
                filesPaths.append(fileInfo.filePath());
            }
        }
    }
    return filesPaths;
}

QStringList detail::getConfigDirs()
{
    $ContextMapStdString paths{"/config/configFilePaths"};
    QStringList ret;
    for(auto pair : *paths){
        ret.append(QString::fromStdString(pair.second));
    }
    return ret;
}

$PackageWebCoreEnd
