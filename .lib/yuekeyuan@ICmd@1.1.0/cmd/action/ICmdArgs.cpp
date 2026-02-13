#include "ICmdArgs.h"
#include "cmd/action/ICmdAction.h"
#include "cmd/ICmdRequest.h"
#include "cmd/ICmdException.h"

$PackageWebCoreBegin

ICmdArgs::ICmdArgs()
{
}

void ICmdArgs::execute(ICmdAction &action, const ICmdRequest &request)
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

bool ICmdArgs::validate(ICmdAction &action, const ICmdRequest &request)
{
    Q_UNUSED(action)
    const auto& values = request.m_arguments;
    if(values.isEmpty()){
        if(!m_nullable){
            throw ICmdException("Args is defined not empty, but the cmd request arguments is empty"
                                + QString(" [Action Path]: ").append(action.m_paths.join(" "))
                                + QString (" [Value Name]: ").append(m_name)
                                );
        }
        return false;
    }
    return true;
}

void ICmdArgs::invokePreMethod(ICmdAction &action, const ICmdRequest &request)
{
    ParamType param;
    param[0] = QMetaType(QMetaType::Void).create();
    param[1] = const_cast<ICmdRequest*>(&request);

    auto index = m_preMethod.methodIndex();
    auto obj = static_cast<QObject*>(action.m_ptr);
    action.m_callable(obj, QMetaObject::InvokeMetaMethod, index, param.data());
    QMetaType(QMetaType::Void).destroy(param[0]);
}

void ICmdArgs::invokePostMethod(ICmdAction &action, const ICmdRequest &request)
{
    ParamType param;
    param[0] = QMetaType(QMetaType::Void).create();
    param[1] = const_cast<ICmdRequest*>(&request);

    auto index = m_postMethod.methodIndex();
    auto obj = static_cast<QObject*>(action.m_ptr);
    action.m_callable(obj, QMetaObject::InvokeMetaMethod, index, param.data());
    QMetaType(QMetaType::Void).destroy(param[0]);
}

void ICmdArgs::invokeSetValueMethod(ICmdAction &action, const ICmdRequest &request)
{
    auto values = request.m_arguments;

    ParamType param;
    param[0] = QMetaType(QMetaType::Void).create();
    param[1] = &values;

    auto index = m_method.methodIndex();
    auto obj = static_cast<QObject*>(action.m_ptr);
    action.m_callable(obj, QMetaObject::InvokeMetaMethod, index, param.data());
    QMetaType(QMetaType::Void).destroy(param[0]);
}

$PackageWebCoreEnd
