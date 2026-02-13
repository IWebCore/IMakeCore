#include "ICmdOption.h"
#include "cmd/ICmdRequest.h"
#include "cmd/action/ICmdAction.h"
#include "cmd/ICmdException.h"

$PackageWebCoreBegin

void ICmdOption::execute(ICmdAction &action, const ICmdRequest &request)
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

bool ICmdOption::validate(ICmdAction &action, const ICmdRequest &request)
{
    Q_UNUSED(action)
    if(!existOption(request)){
        if(m_isRequired){
            throw ICmdException("Option is required but your cmd is not include this option. "
                                + QString(" [Option Name]: ").append(m_name));
        }else{
            return false;
        }
    }
    return true;
}

void ICmdOption::invokePreMethod(ICmdAction &action, const ICmdRequest &request)
{
    ParamType param;
    param[0] = QMetaType(QMetaType::Void).create();
    param[1] = const_cast<ICmdRequest*>(&request);

    auto index = m_preMethod.methodIndex();
    auto obj = static_cast<QObject*>(action.m_ptr);
    action.m_callable(obj, QMetaObject::InvokeMetaMethod, index, param.data());
    QMetaType(QMetaType::Void).destroy(param[0]);
}

void ICmdOption::invokePostMethod(ICmdAction &action, const ICmdRequest &request)
{
    ParamType param;
    param[0] = QMetaType(QMetaType::Void).create();
    param[1] = const_cast<ICmdRequest*>(&request);

    auto index = m_postMethod.methodIndex();
    auto obj = static_cast<QObject*>(action.m_ptr);
    action.m_callable(obj, QMetaObject::InvokeMetaMethod, index, param.data());
    QMetaType(QMetaType::Void).destroy(param[0]);
}

void ICmdOption::invokeSetValueMethod(ICmdAction &action, const ICmdRequest &request)
{
    bool m_value = existOption(request);
    m_property.writeOnGadget(action.m_ptr, m_value);
}

bool ICmdOption::existOption(const ICmdRequest &request) const
{
    QString shortName = "-" + m_shortName;
    QString fullName = "--" + m_name;
    return request.m_options.contains(shortName) || request.m_options.contains(fullName);
}

$PackageWebCoreEnd
