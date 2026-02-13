#pragma once

#include "core/util/IHeaderUtil.h"
#include "core/base/IResult.h"
#include <sstream>
#if  __has_include(<charconv>)
    #include <charconv>
#endif

$PackageWebCoreBegin

namespace  IConvertUtil
{
    template<typename T>
    bool toNumber(T&val, const std::string& data);

    QDate toDate(const QString& val, bool& ok);
    QTime toTime(const QString& val, bool& ok);
    QDateTime toDateTime(const QString& val, bool& ok);
    QString toUtcString(const QDateTime& dateTime);


    // TODO: pre GCC11 should deal specially latter!!!
    // NOTE: 第二种方法对于 ulonglong 的处理不对，有溢出的问题
#if __has_include(<charconv>)
    template <typename T>
    T stringToNumber(const std::string& str, bool& ok)
    {
        if (str.empty()) {
            ok = false;
            return {};
        }
        T result{};
        if constexpr (std::is_integral_v<T>){
            auto val = std::from_chars(str.data(), str.data()+str.length(), result);
            if (val.ec != std::errc()) {
                ok = false;
                return {};
            }
        }else if constexpr(std::is_floating_point_v<T>){
            std::istringstream iss(str);
            iss >> result;
            if (iss.fail() || !iss.eof()) {
                ok = false;
                return {};
            }
        }else{
            static_assert(std::is_arithmetic_v<T>, "T must be an arithmetic type");
            ok = false;
        }
        ok = true;
        return result;
    }
#else
    template <typename T>
    T stringToNumber(const std::string& str, bool& ok)
    {
        ok = true;
        try{
            if constexpr (std::is_same_v<T, double>){
                return std::stod(str);
            }
            if constexpr (std::is_same_v<T, float>){
                return std::stof(str);
            }
            if constexpr (std::is_signed_v<T>){
                auto value = std::stoll(str);
                if(value > std::numeric_limits<T>::max() || value < std::numeric_limits<T>::min()){
                    ok = false;
                    return {};
                }
                return value;
            }
            if constexpr (! std::is_signed_v<T>){
                auto value = std::stoull(str);
                if(value > std::numeric_limits<T>::max() || value < std::numeric_limits<T>::min()){
                    ok = false;
                    return {};
                }
                return value;
            }
        }catch(...){
            ok = false;
            return {};
        }
        ok = false;
        return {};
    }
#endif
}

$PackageWebCoreEnd
