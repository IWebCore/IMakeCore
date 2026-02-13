#include "ICmdOptionValue.h"
#include "cmd/action/ICmdAction.h"
#include "cmd/ICmdRequest.h"
#include "cmd/ICmdException.h"

$PackageWebCoreBegin

void ICmdOptionValue::execute(ICmdAction &action, const ICmdRequest &request)
{
    if(!validate(action, request)){
        return;
    }

    if(m_preMethod.isValid()){
        invokePreMethod(action, request);
    }

    invokeSetValueMethod(action, request);

    if(m_postMethod.isValid()){
        invokePostMethod(action, request);
    }
}

bool ICmdOptionValue::validate(ICmdAction &action, const ICmdRequest &request)
{
    Q_UNUSED(action)
    auto values = getOptionValues(request);
    if(values.isEmpty()){
        return false;
    }
    return true;
}

void ICmdOptionValue::invokePreMethod(ICmdAction &action, const ICmdRequest &request)
{
    ParamType param;
    param[0] = QMetaType(QMetaType::Void).create();
    param[1] = const_cast<ICmdRequest*>(&request);

    auto index = m_preMethod.methodIndex();
    auto obj = static_cast<QObject*>(action.m_ptr);
    action.m_callable(obj, QMetaObject::InvokeMetaMethod, index, param.data());
    QMetaType(QMetaType::Void).destroy(param[0]);
}

void ICmdOptionValue::invokePostMethod(ICmdAction &action, const ICmdRequest &request)
{
    ParamType param;
    param[0] = QMetaType(QMetaType::Void).create();
    param[1] = const_cast<ICmdRequest*>(&request);

    auto index = m_postMethod.methodIndex();
    auto obj = static_cast<QObject*>(action.m_ptr);
    action.m_callable(obj, QMetaObject::InvokeMetaMethod, index, param.data());
    QMetaType(QMetaType::Void).destroy(param[0]);
}

void ICmdOptionValue::invokeSetValueMethod(ICmdAction &action, const ICmdRequest &request)
{
    auto values = getOptionValues(request);

    ParamType param;
    param[0] = QMetaType(QMetaType::Void).create();
    param[1] = &values;

    auto index = m_method.methodIndex();
    auto obj = static_cast<QObject*>(action.m_ptr);
    action.m_callable(obj, QMetaObject::InvokeMetaMethod, index, param.data());
    QMetaType(QMetaType::Void).destroy(param[0]);
}

QStringList ICmdOptionValue::getOptionValues(const ICmdRequest &request) const
{
    auto fullName = "--" + m_name;
    if(m_shortName.isEmpty()){
        if(request.m_options.contains(fullName)){
            return request.m_options[fullName];
        }
        return {};
    }

    QStringList ret;
    if(request.m_options.contains(fullName)){
        ret = request.m_options[fullName];
    }
    auto shortName = "-" + m_shortName;
    if(request.m_options.contains(shortName)){
        auto opts = request.m_options[shortName];
        for(auto opt : opts){
            ret.append(opt);
        }
    }
    return ret;
}

$PackageWebCoreEnd
