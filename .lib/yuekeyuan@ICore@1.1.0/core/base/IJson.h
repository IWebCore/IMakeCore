#pragma once

#include <QString>
#include <QMetaType>
#include <json.hpp>
#include <string>

#ifndef IJSON_REGISTER_INFO
#define IJSON_REGISTER_INFO

using IJson = nlohmann::json;

Q_DECLARE_METATYPE(IJson)

Q_DECLARE_METATYPE(std::string)


namespace nlohmann
{
template <>
struct adl_serializer<QString>
{
    static QString from_json(const IJson& j)
    {
        if(j.is_string()){
            return QString::fromStdString(j.template get<std::string>());
        }
        return QString::fromStdString(j.dump());
    }

    static void to_json(IJson& j, const QString& str)
    {
        j = str.toStdString();
    }
};
}

#endif
