#pragma once

#include "core/util/ITraitUtil.h"

$PackageWebCoreBegin

namespace IMetaUtil
{
    const char* getMetaClassName(const QMetaObject& meta);

    QMap<QString, QString> getMetaClassInfoMap(const QMetaObject& meta);  // resolve for Q_GADGET

    QString getMetaClassInfoByName(const QMetaObject& meta, const QString& name, const QString& defaultVal = "");
    QString getMetaClassInfoByName(const QMap<QString, QString>& map, const QString& name, const QString& defaultVal = "");

    QVector<QMetaProperty> getMetaProperties(const QMetaObject &meta);

    QVector<QMetaMethod> getMetaMethods(const QMetaObject& meta);

    bool writeProperty(const QMetaProperty& prop, void* handler,  const QVariant& value);
    QVariant readProperty(const QMetaProperty& prop, const void* handler);

    template<typename T>
    QSet<int> registMetaType(QStringList names={});

    template<typename T>
    const std::string& getBareTypeName();

    template<typename T>
    const QString& getTypeName();

    const char* typeName(int id);

    inline auto typeId(const QVariant& id)
    {
#if QT_VERSION < QT_VERSION_CHECK(6, 0, 0)
        return id.type();
#else
        return id.typeId();
#endif
    }

    inline auto typeId (const QMetaProperty& prop)
    {
#if QT_VERSION < QT_VERSION_CHECK(6, 0, 0)
        return prop.type();
#else
        return prop.typeId();
#endif
    }

    inline auto typeId(const QByteArray& typeName)
    {
#if QT_VERSION < QT_VERSION_CHECK(6, 0, 0)
        return QMetaType::type(typeName);
#else
        return QMetaType::fromName(typeName).id();
#endif
    }

    QString demangleName(const char*);
}

template<typename T>
QSet<int> IMetaUtil::registMetaType(QStringList names)
{
    static QSet<int> s_id;
    static std::once_flag flag;
    std::call_once(flag, [=](){
        auto names_ = names;
        if(names_.isEmpty()){
            QString name = QString::fromStdString(getBareTypeName<T>());

            names_.append(name);
            if(!name.startsWith("std::")){
                if(name.contains("::")){
                    names_.append(name.split("::").last());
                }
            }
        }

        for(auto name : names_){
            s_id << qRegisterMetaType<T>(name.toUtf8());
            s_id << qRegisterMetaType<T>(QString((name + "&")).toUtf8());
        };
    });
    return s_id;
}

template<typename T>
const std::string& IMetaUtil::getBareTypeName()
{
    if constexpr( std::is_same_v<T, std::string>){
        static const std::string name = "std::string";
        return name;
    }else if constexpr (std::is_same_v<T, IString>){
        static const std::string name = "IString";
        return name;
    }else if constexpr (std::is_same_v<T, QString>){
        static const std::string name = "QString";
        return name;
    }

    static std::string s_name;
    if(s_name.empty()){
        QString name = demangleName(typeid(T).name());
        if(name.startsWith("class ")){
            name = name.mid(6);
        }
        if(name.startsWith("struct ")){
            name = name.mid(7);
        }
        s_name = name.replace("<class ", "<").replace(",class ", ", ").toStdString();
    }
    return s_name;
}

template<typename T>
const QString& IMetaUtil::getTypeName()
{
    static const QString& name = QString::fromStdString(IMetaUtil::getBareTypeName<T>());
    return name;
}

$PackageWebCoreEnd
