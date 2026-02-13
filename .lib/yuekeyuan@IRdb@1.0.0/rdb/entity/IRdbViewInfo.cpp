#include "IRdbViewInfo.h"
#include "core/util/IMetaUtil.h"

$PackageWebCoreBegin

namespace detail
{
    void processNotations(const QMap<QString, QString>& clsInfo, IRdbViewInfo& viewInfo);
    bool setCreateViewSql(const QString& key, const QString& value, IRdbViewInfo& viewInfo);

    void processChecks(const QMap<QString, QString>& clsInfo, const IRdbViewInfo& viewInfo);
}

IRdbViewInfo::IRdbViewInfo(const QMetaObject &meta) : IRdbEntityInfo(meta)
{
   auto clsInfo = IMetaUtil::getMetaClassInfoMap(meta);
   detail::processNotations(clsInfo, *this);
   detail::processChecks(clsInfo, *this);
}

void detail::processNotations(const QMap<QString, QString> &clsInfo, IRdbViewInfo &viewInfo)
{
    using NotationFun = std::function<bool(const QString&, const QString&, IRdbViewInfo&)>;
    static QList<NotationFun> notationFun = {
        detail::setCreateViewSql,
    };

    for(const auto& name : clsInfo.keys()){
        for(auto fun : notationFun){
            if(fun(name, clsInfo[name], viewInfo)){
                break;
            }
        }
    }
}

bool detail::setCreateViewSql(const QString &key, const QString &value, IRdbViewInfo &view)
{
    static const char* const PREFIX = "sql_createViewSql";
    if(key == PREFIX){
        view.m_createViewSql = value;
        return true;
    }
    return false;
}

void detail::processChecks(const QMap<QString, QString> &clsInfo, const IRdbViewInfo &viewInfo)
{
    Q_UNUSED(clsInfo)
    Q_UNUSED(viewInfo)
}

$PackageWebCoreEnd
