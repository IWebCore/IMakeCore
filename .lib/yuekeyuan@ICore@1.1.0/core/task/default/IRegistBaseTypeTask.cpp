#include "IRegistBaseTypeTask.h"

$PackageWebCoreBegin

namespace detail
{
    template<typename T>
    void registerBaseType(const QString &name){
        qRegisterMetaType<T>(name.toUtf8());
        qRegisterMetaType<T>(QString((name + "&")).toUtf8());
    }

    void registerNumberType();
    void registerStringConverter();
}

void IRegistBaseTypeTask::$task()
{
    detail::registerNumberType();
    detail::registerStringConverter();
}

void detail::registerNumberType()
{
#ifdef REGIST_TYPE_DEF
    #error macro duplicated
#endif
#define REGIST_TYPE_DEF(type)   \
    registerBaseType<type>( #type );

    REGIST_TYPE_DEF(uchar)
    REGIST_TYPE_DEF(ushort)
    REGIST_TYPE_DEF(uint)
    REGIST_TYPE_DEF(ulong)
    REGIST_TYPE_DEF(int8_t)
    REGIST_TYPE_DEF(std::int8_t)
    REGIST_TYPE_DEF(uint8_t)
    REGIST_TYPE_DEF(std::uint8_t)
    REGIST_TYPE_DEF(int16_t)
    REGIST_TYPE_DEF(std::int16_t)
    REGIST_TYPE_DEF(uint16_t)
    REGIST_TYPE_DEF(std::uint16_t)
    REGIST_TYPE_DEF(int32_t)
    REGIST_TYPE_DEF(std::int32_t)
    REGIST_TYPE_DEF(uint32_t)
    REGIST_TYPE_DEF(std::uint32_t)
    REGIST_TYPE_DEF(int64_t)
    REGIST_TYPE_DEF(std::int64_t)
    REGIST_TYPE_DEF(uint64_t)
    REGIST_TYPE_DEF(std::uint64_t)
#undef REGIST_TYPE_DEF

    registerBaseType<qlonglong>("qlonglong");
    registerBaseType<qulonglong>("qulonglong");
    registerBaseType<long long>("longlong");
    registerBaseType<unsigned long long>("ulonglong");
}

void detail::registerStringConverter()
{
    QMetaType::registerConverter<QString, IString>([](const QString& data){
        return IString(data.toUtf8());
    });
    QMetaType::registerConverter<IString, QString>([](const IString& data){
        return data.toQString();
    });

    QMetaType::registerConverter<QString, std::string>([](const QString& data){
        return data.toStdString();
    });
    QMetaType::registerConverter<std::string, QString>([](const std::string& data){
        return QString::fromStdString(data);
    });

    QMetaType::registerConverter<IString, std::string>([](const IString& data){
        return data.toStdString();
    });
    QMetaType::registerConverter<std::string, IString>([](const std::string& data){
        return IString(data);
    });
}

$PackageWebCoreEnd
