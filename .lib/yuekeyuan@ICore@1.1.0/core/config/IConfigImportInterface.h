#pragma once

#include "core/util/IHeaderUtil.h"
#include "core/config/IConfigAbort.h"
#include "core/config/IConfigManageInterface.h"
#include "core/unit/IStackObjectUnit.h"
#include "core/unit/ISoloUnit.h"

$PackageWebCoreBegin

template<typename T>
class IConfigImportInterface : public IStackObjectUnit
{
public:
    enum class ValueType : uint8_t{
        InitializedValue,
        DefaultValue,
        LoadedValue
    };
    struct ValueMark{
        ValueType valueType{ValueType::InitializedValue};
        bool isLoaded{false};
        bool isFound {false};
    };

protected:
    explicit IConfigImportInterface(const QString& path);
    explicit IConfigImportInterface(const char* path);
    explicit IConfigImportInterface(std::string path);
    explicit IConfigImportInterface(const QString& path, T value);
    explicit IConfigImportInterface(const char* path, T value);
    explicit IConfigImportInterface(std::string path, T value);

public:
    bool operator !=(const T& value) const;
    const T& value() const;
    const T& operator *() const;

public:
    bool isInitializedValue() const;
    bool isDefaultedValue() const;
    bool isLoadedValue() const;

private:
    const std::string& path();

protected:
    virtual IConfigManageInterface& getConfigManage() const = 0;

private:
    const T& get() const;

protected:
    std::string m_path;
    mutable T m_data {};
    mutable ValueMark m_valueMark{};
};


template<typename T>
IConfigImportInterface<T>::IConfigImportInterface(const QString &path)
    : IConfigImportInterface(path.toStdString())
{
}

template<typename T>
IConfigImportInterface<T>::IConfigImportInterface(const char *path)
    : IConfigImportInterface<T>(std::string(path))
{
}

template<typename T>
IConfigImportInterface<T>::IConfigImportInterface(const QString &path, T value)
    : IConfigImportInterface(path.toStdString(), std::forward<T>(value))
{
}

template<typename T>
IConfigImportInterface<T>::IConfigImportInterface(const char *path, T value)
    : IConfigImportInterface(std::string(path), std::forward<T>(value))
{
}

template<typename T>
IConfigImportInterface<T>::IConfigImportInterface(std::string path)
    : m_path(std::move(path))
{
    m_valueMark.valueType = ValueType::InitializedValue;

    std::replace(m_path.begin(), m_path.end(), '.', '/');
    if (m_path.empty() || m_path[0] != '/') {
        m_path.insert(m_path.begin(), '/');
    }
}

template<typename T>
IConfigImportInterface<T>::IConfigImportInterface(std::string path, T value)
    : m_path(std::move(path)), m_data(std::move(value))
{
    m_valueMark.valueType = ValueType::DefaultValue;

    std::replace(m_path.begin(), m_path.end(), '.', '/');
    if (m_path.empty() || m_path[0] != '/') {
        m_path.insert(m_path.begin(), '/');
    }
}

template<typename T>
bool IConfigImportInterface<T>::operator !=(const T &value) const
{
    return get() != value;
}

template<typename T>
const T &IConfigImportInterface<T>::value() const
{
    return get();
}

template<typename T>
const T& IConfigImportInterface<T>::operator *() const
{
    return get();
}

template<typename T>
bool IConfigImportInterface<T>::isInitializedValue() const
{
    return !isLoadedValue() && (m_valueMark.valueType == ValueType::InitializedValue);
}

template<typename T>
bool IConfigImportInterface<T>::isDefaultedValue() const
{
    return !isLoadedValue() && (m_valueMark.valueType == ValueType::DefaultValue);
}

template<typename T>
bool IConfigImportInterface<T>::isLoadedValue() const
{
    get();
    return m_valueMark.isLoaded && m_valueMark.isFound;
}

template<typename T>
const std::string &IConfigImportInterface<T>::path()
{
    return m_path;
}

template<typename T>
const T &IConfigImportInterface<T>::get() const
{
    if(m_valueMark.isLoaded){
        return m_data;
    }

    IJson value = getConfigManage().getConfig(m_path);
    if(value.is_null()){
        m_valueMark.isFound = false;
        return m_data;
    }
    // IJson
    if constexpr (std::is_same_v<T, IJson>){
        m_valueMark.isFound = true;
        m_data = value;
    }
    // bool
    else if constexpr (std::is_same_v<T, bool>){
        m_valueMark.isFound = value.is_boolean();
        if(m_valueMark.isFound){
            m_valueMark.isFound = true;
            m_data = value.get<bool>();
        }
    }
    // signed
    else if constexpr (std::is_integral_v<T> && std::is_signed_v<T>){
        m_valueMark.isFound = value.is_number();
        if(m_valueMark.isFound){
            m_data = value.get<int64_t>();
        }
    }
    // unsigned
    else if constexpr (std::is_integral_v<T> && !std::is_signed_v<T>){
        m_valueMark.isFound = value.is_number();
        if(m_valueMark.isFound){
            m_data = value.get<uint64_t>();
        }
    }
    // floating point
    else if constexpr (std::is_floating_point_v<T>){
        m_valueMark.isFound = value.is_number();
        if(m_valueMark.isFound){
            m_data = value.get<double>();
        }
    }
    // std::string
    else if constexpr (std::is_same_v<std::string, T>){
        m_valueMark.isFound = value.is_string();
        if(m_valueMark.isFound){
            m_data = value.get<std::string>();
        }
    }
    // QString
    else if constexpr (std::is_same_v<QString, T>){
        m_valueMark.isFound = value.is_string();
        if(m_valueMark.isFound){
            m_data = QString::fromStdString(value.get<std::string>());
        }
    }
    // QStringList
    else if constexpr (std::is_same_v<QStringList, T>){
        auto found = value.is_array();
        if(found){
            for(const auto& val : value){
                if(val.is_string()){
                    m_data.append(QString::fromStdString(val.get<std::string>()));
                }else{
                    IConfigAbort::abortConvertToStringTypeError("error, not all value are string", $ISourceLocation);
                }
            }
            m_valueMark.isFound = true;
        }
    }
    // std::map<std::string, std::string>
    else if constexpr (std::is_same_v<std::map<std::string, std::string>, T>){
        auto found = value.is_object();
        if(found){
            for(auto it=value.begin(); it!= value.end(); it++){
                if(it.value().is_string()){
                    m_data[it.key()] = it.value().get<std::string>();
                }else{
                    IConfigAbort::abortConvertToStringTypeError("not all value are std::string");
                }
            }
            m_valueMark.isFound = true;
        }
    }
    else {
        QString tip = QString("type:").append(IMetaUtil::getTypeName<T>());
        IConfigAbort::abortConvertTypeNotImplimented(tip, $ISourceLocation);
    }

    m_valueMark.isLoaded = true;
    return m_data;
}

$PackageWebCoreEnd
