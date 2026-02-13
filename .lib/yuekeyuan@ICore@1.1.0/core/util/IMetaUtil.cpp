#include "IMetaUtil.h"
#include <vector>

$PackageWebCoreBegin

const char* IMetaUtil::getMetaClassName(const QMetaObject &meta)
{
    return meta.className();
}

QMap<QString, QString> IMetaUtil::getMetaClassInfoMap(const QMetaObject& meta)
{
    QMap<QString, QString> ret;
    int count = meta.classInfoCount();
    for(int i=0; i<count; i++){
        auto info = meta.classInfo(i);
        ret[info.name()] = info.value();
    }
    return ret;
}

QString IMetaUtil::getMetaClassInfoByName(const QMetaObject &meta, const QString &name, const QString &defaultVal)
{
    auto metaClsInfo = getMetaClassInfoMap(meta);
    return getMetaClassInfoByName(metaClsInfo, name, defaultVal);
}

QString IMetaUtil::getMetaClassInfoByName(const QMap<QString, QString> &map, const QString &name, const QString &defaultVal)
{
    if(map.contains(name)){
        return map[name];
    }
    return defaultVal;
}

QVector<QMetaMethod> IMetaUtil::getMetaMethods(const QMetaObject &meta)
{
    QVector<QMetaMethod> ret;
    auto count = meta.methodCount();
    for(int i=0; i<count; i++){
        ret.append(meta.method(i));
    }
    return ret;
}

QVector<QMetaProperty> IMetaUtil::getMetaProperties(const QMetaObject &meta)
{
    QVector<QMetaProperty> ret;
    auto count = meta.propertyCount();
    for(int i=0; i<count; i++){
        ret.push_back(meta.property(i));
    }
    return ret;
}

bool IMetaUtil::writeProperty(const QMetaProperty &prop, void *handler, const QVariant &value)
{
    Q_ASSERT(!QString(prop.name()).isEmpty());
    if(prop.isWritable()){
        prop.writeOnGadget(handler, value);
        return true;
    }
    return false;
}

QVariant IMetaUtil::readProperty(const QMetaProperty &prop, const void *handler)
{
    return prop.readOnGadget(handler);
}

const char *IMetaUtil::typeName(int id)
{
#if QT_VERSION < QT_VERSION_CHECK(6, 0, 0)
    return QMetaType::typeName(id);
#else
    return QMetaType(id).name();
#endif
}


#if defined(__GNUC__)
    # include <cxxabi.h>
#elif defined(__clang__)

#elif defined(_MSC_VER)
    #include <windows.h>
    #include <dbghelp.h>
    #pragma comment ( lib,"DbgHelp.lib" )
#endif

QString IMetaUtil::demangleName(const char *name)
{
#ifdef __GNUC__
    int status;
     char* demangledName = abi::__cxa_demangle(name, nullptr, nullptr, &status);
     if(status == 0){
         return demangledName;
     }else{
         return name;
     }
#elif defined(__clang__)
    qDebug() << "this should be test when clang applied";
    return name;
#elif defined(_MSC_VER)
    char* demangledName = nullptr;
    HRESULT result = UnDecorateSymbolName(name, demangledName, 0, UNDNAME_COMPLETE);
    if (result == S_OK && demangledName != nullptr) {
        std::string temp(demangledName);
        free(demangledName);
        return QString::fromStdString(temp);
    } else {
        return name;
    }
#else
    return name;
#endif
}

$PackageWebCoreEnd
