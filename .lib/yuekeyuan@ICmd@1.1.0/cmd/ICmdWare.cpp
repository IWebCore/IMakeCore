#include "ICmdWare.h"
#include "cmd/ICmdManage.h"
#include "cmd/ICmdException.h"
#include "cmd/action/ICmdAction.h"
#include "cmd/action/ICmdArgs.h"
#include "cmd/action/ICmdArgx.h"
#include "cmd/action/ICmdOptionValue.h"
#include "cmd/action/ICmdOption.h"

$PackageWebCoreBegin

void ICmdWare::parseAction(void *ptr, const QString& clsName, const QMap<QString, QString> &infos, const QVector<QMetaMethod> &methods, const QVector<QMetaProperty>& props)
{
    m_ptr = ptr;
    m_className = clsName;
    m_info = infos;
    m_methods = methods;
    m_props = props;

    try{
        findPrePath();
        findOption();
        findOptionValues();
        findArgs();
        findArgx();
        createActions();
    } catch(const ICmdException& e){
        qDebug() << e.getCause();
        throw e;
    }
}

void ICmdWare::findPrePath()
{
    QMap<int, QString> pathMap;
    const QString prefix = "IAsCmdClassMapping$$$";
    for(const auto& key : m_info.keys()){
        if(key.startsWith(prefix)){
            pathMap[key.mid(prefix.length()).toInt()] = m_info[key];
        }
    }
    for(int i=1; i<=pathMap.size(); i++){
        m_prePaths.append(pathMap[i]);
    }
    if(m_prePaths.length() == 1){
        QString path = m_prePaths.first();
        if(path.trimmed().isEmpty() || path == "/"){
            m_prePaths.clear();
        }
    }
}


void ICmdWare::findOption()
{
    QString position = QString(" [Class]: ").append(m_className);

    QStringList options;
    for(auto key : m_info.keys()){
        if(key.startsWith("ICmdOption$$$")){
            options.append(m_info[key]);
        }
    }

    for(const auto& name : options){
        auto option = new ICmdOption();
        option->m_name = name;
        option->m_memo = m_info.value("ICmdOptionMemo$$$" + name);
        option->m_shortName = m_info.value("ICmdOptionShortName$$$" + name);
        auto noValueName = "ICmdOptionNoValue$$$" + name;
        option->m_isNoValue = m_info.contains(noValueName) && m_info.value(noValueName) == "true";
        auto requiredName = "ICmdOptionRequired$$$" + name;
        option->m_isRequired = m_info.contains(requiredName) && (m_info.value(requiredName) == "true");
        option->m_property = findProperty(name);
        option->m_preMethod = findPreHandleMethod("ICmdOptionPreHandle$$$" + name,
            "Option PreHandle function is defined, but function not found. "
            + QString(" [Option Name]: ").append(option->m_name) + position);
        option->m_postMethod = findPostHandleMethod("ICmdOptionPostHandle$$$" + name,
            "Option PostHandle function is defined, but function not found. "
            + QString(" [Option Name]: ").append(name).append(" [Defined Function]: ").append(name)  + position );

        checkOptionMethod(option);
        m_options.append(option);
    }
    checkOptionShortNameComflict();
}

void ICmdWare::findOptionValues()
{
    QString position = QString(" [Class]: ").append(m_className);

    QMap<ICmdOption*, QStringList> map;
    for(auto option : m_options){
        auto str = "ICmdOptionValue$$$" + option->m_name + "$$$";
        for(const QString& key : m_info.keys()){
            if(key.startsWith(str)){
                map[option].append(m_info[key]);
            }
        }
    }

    for(auto opt : map.keys()){
        for(const QString& name : map[opt]){
            auto optionValue = new ICmdOptionValue();
            if(opt->m_isNoValue){
                throw ICmdException("Option is defined as no values. but OptionValue attached to this Option"
                                    + QString(" [Option]: ").append(opt->m_name)
                                    + QString(" [Option Name]: ").append(name) + position);
            }

            optionValue->m_option = opt;
            optionValue->m_name = opt->m_name;
            optionValue->m_shortName = opt->m_shortName;
            optionValue->m_valueName = name;
            optionValue->m_memo = m_info.value("ICmdOptionValueMemo$$$" + name);
            auto nullableName = "ICmdOptionValueNullable$$$" + name;
            optionValue->m_nullable = m_info.contains(nullableName) &&  m_info.value(nullableName) == "true";
            optionValue->m_prop = findProperty(name);
            optionValue->m_method = findSetValueMethod(name,
                "Cmd Option values must have its $set_value_xxx method. " + QString(" [Option Name]: ").append(name)  + position
            );
            optionValue->m_preMethod = findPreHandleMethod("ICmdOptionValuePreHandle$$$" + name,
                "Option PreHandle function is defined, but function not found. "
                + QString(" [Option Name]: ").append(name).append(" [Defined Function]: ").append(name)  + position);
            optionValue->m_postMethod = findPostHandleMethod("ICmdOptionValuePostHandle$$$" + name,
                 "Option PostHandle function is defined, but function not found. "
                + QString(" [Option Name]: ").append(name).append(" [Defined Function]: ").append(name)  + position
            );

            checkOptionValueMethod(optionValue);
            m_optionValues.append(optionValue);
        }
    }
}

void ICmdWare::findArgs()
{
    QStringList names;
    for(const QString& key : m_info.keys()){
        if(key.startsWith("ICmdArgsArgument$$$")){
            names.append(m_info[key]);
        }
    }
    if(names.length() == 0){
        return;
    }
    if(names.length() > 1){
        throw ICmdException("$CmdArgs must be only at most one. " + QString(" [Class]: ").append(m_className));
    }

    QString name = names.first();
    QString position = QString(" [Class]: ").append(m_className).append(" [Args Name]: ").append(name);

    // prop, name
    m_args = new ICmdArgs;
    m_args->m_name = name;
    m_args->m_memo = m_info.value("ICmdArgsMemo$$$" + name);
    m_args->m_nullable = m_info.contains("ICmdArgsNullable$$$" + name);
    m_args->m_method = findSetValueMethod(name, "Action Args property is not exist. " + position);
    m_args->m_prop = findProperty(name);
    m_args->m_preMethod = findPreHandleMethod("ICmdArgsPreHandle$$$" + name,
        "option prehandle is define, but function not valid. " + position);
    m_args->m_postMethod = findPostHandleMethod("ICmdArgsPostHandle$$$" + name,
        "option posthandle is define, but function not valid. " + position);

    checkArgsMethod();
}

void ICmdWare::findArgx()
{
    QString position = QString(" [Class]: ").append(m_className);
    QMap<int, QString> map;
    for(const QString& key : m_info.keys()){
        if(key.startsWith("ICmdArgXArgument$$$")){
            auto index = key.split("$$$")[1].toInt();
            auto name = m_info[key];
            if(map.contains(index)){
                throw ICmdException("argx index conflict. " + QString(" [index]: ").append(QString::number(index)) + position);
            }
            if(map.values().contains(name)){
                throw ICmdException("argx name duplicated. " + QString(" [name]: ").append(name) + position);
            }
            map[index] = m_info[key];
        }
    }

    for(auto index: map.keys()){
        auto name = map[index];
        auto argx = new ICmdArgx;
        argx->m_index = index;
        argx->m_name = name;
        argx->m_property = findProperty(name);
        argx->m_method = findSetValueMethod(name, "argx set_set_value method not found");
        argx->m_memo = m_info.value("ICmdArg" + QString::number(argx->m_index) + "Memo$$$");
        QString nullableName = "ICmdArgXNullable$$$" + QString::number(argx->m_index);
        argx->m_nullable = m_info.contains(nullableName) && m_info[nullableName] == "true";
        auto preHandleFun = "ICmdArgXPreHandle$$$" + QString::number(argx->m_index);
        argx->m_preMethod = findPreHandleMethod(preHandleFun,
            "argx PreHandle function is define, but function not valid"
                                                + QString(" [name]: ").append(name)
                                                + QString(" [index]: ").append(QString::number(index))
                                                + QString(" [PreHandle function]: ").append(preHandleFun)
                                                + position);
        auto postHandleFun = "ICmdArgXPostHandle$$$" + QString::number(argx->m_index);
        argx->m_postMethod = findPostHandleMethod( postHandleFun,
            "argx PostHandle function is define, but function not valid"
                                                + QString(" [name]: ").append(name)
                                                + QString(" [index]: ").append(QString::number(index))
                                                + QString(" [PostHandle function]: ").append(postHandleFun)
                                                + position);



        checkArgxMethod(argx);
        this->m_argxes.append(argx);
    }
}

void ICmdWare::createActions()
{
    const QString prefix = "IAsCmdMethodMapping$$$";
    for(const auto& key : m_info.keys()){
        if(key.startsWith(prefix)){
            createAction(key);
        }
    }
}

void ICmdWare::createAction(const QString &key)
{
    auto funName = m_info[key];
    auto action = new ICmdAction;
    action->m_ptr = m_ptr;
    action->m_memo = getActionMemo(funName);
    action->m_paths = getActionPaths(funName);
    action->m_method = getActionMethod(funName);
    action->m_callable = (static_cast<IGadgetUnit*>(m_ptr))->staticMetaCallFunction();
    action->m_optionValues = m_optionValues;
    action->m_options = m_options;
    action->m_args = m_args;
    action->m_argxes = m_argxes;

    checkActionMethod(action);
    ICmdManage::instance().registAction(action);
}

QStringList ICmdWare::getActionPaths(const QString &funName)
{
    QString prefix = QString("IAsCmdMethodArgMapping$$$").append(funName).append("$$$");
    QMap<int, QString> paths;
    for(const auto& key : m_info.keys()){
        if(key.startsWith(prefix)){
            paths[key.mid(prefix.length()).toInt()] = m_info[key];
        }
    }
    QStringList ret = m_prePaths;
    for(int i=1; i<=paths.size(); i++){
        if(paths[i] != "/"){
            ret.append(paths[i]);
        }
    }

    return ret;
}

QMetaMethod ICmdWare::getActionMethod(const QString &funName)
{
    for(const QMetaMethod& method : m_methods){
        if(method.name() == funName){
            return method;
        }
    }
    return {};
}

QString ICmdWare::getActionMemo(const QString &funName)
{
    auto memoString = "ICmdMappingMemo$$$" + funName;
    return m_info.value(memoString);
}

QMetaMethod ICmdWare::findSetValueMethod(const QString &name, const QString &failReason)
{
    QString setName = "$set_value_" +  name;
    for(const QMetaMethod& method : m_methods){
        if(method.name() == setName){
            return method;
        }
    }
    throw ICmdException(failReason);
    return {};
}

QMetaMethod ICmdWare::findPreHandleMethod(const QString &optionPre, const QString &failReason)
{
    if(m_info.contains(optionPre)){
        auto name = m_info[optionPre];
        for(const QMetaMethod&method : m_methods){
            if(method.name() == name){
                return method;
            }
        }
        throw ICmdException(failReason);
    }
    return {};
}

QMetaMethod ICmdWare::findPostHandleMethod(const QString &optionPost, const QString &failReason)
{
    if(m_info.contains(optionPost)){
        auto name = m_info[optionPost];
        for(const QMetaMethod&method : m_methods){
            if(method.name() == name){
                return method;
            }
        }
        throw ICmdException(failReason);
    }
    return {};
}

QMetaProperty ICmdWare::findProperty(const QString &name)
{
    for(const QMetaProperty& prop : m_props){
        if(prop.name() == name){
            return prop;
        }
    }
    return {};
}

void ICmdWare::checkActionMethod(ICmdAction *action)
{
    QString position = QString(" [Mapping Path]: ").append(action->m_paths.join(" "))
            .append(" [FunctionName]: ").append(action->m_method.name())
            .append(" [Class]: ").append(m_className);

    if(!action->m_method.isValid()){
        throw ICmdException("action mapping method is not valid. " + position);
    }

    if(action->m_method.returnType() != QMetaType::Void){
        throw ICmdException("action mapping method return type must be void. " + position);
    }

    auto argTypes = getMethodArguments(action->m_method);
    if(argTypes.length() > 1){
        throw ICmdException("action mapping method arguments count should be one or zero. " + position);
    }
    if(argTypes.length() == 1){
        if(argTypes.first() != "ICmdRequest" || argTypes.first() != "ICmdRequest&" ){
            throw ICmdException("action mapping method arguments type can only be ICmdRequest. " + position);
        }
    }

    if(action->m_paths.isEmpty()){
        throw ICmdException("action mapping path can not be none. " + position);
    }

    for(const QString& path : action->m_paths){
        if(path.trimmed().isEmpty()){
            throw ICmdException("action mapping path can not be empty. " + position);
        }
    }
}

void ICmdWare::checkOptionMethod(ICmdOption *option)
{
    QString position = QString(" [Class]: ").append(m_className).append(" [Option Name]: ").append(option->m_name);

    if(!option->m_property.isValid()){
        throw ICmdException("Option property is not valid. "
                            + position);
    }
    if(option->m_postMethod.isValid()){
        checkHandleMethod(option->m_postMethod);
    }
    if(option->m_preMethod.isValid()){
        checkHandleMethod(option->m_preMethod);
    }
}

void ICmdWare::checkOptionValueMethod(ICmdOptionValue *option)
{
    QString position = QString(" [Class]: ").append(m_className).append(" [Option Name]: ").append(option->m_name);

    if(!option->m_method.isValid()){
        throw ICmdException("Option $set_value_xxx method is not valid. " + position);
    }
    if(option->m_preMethod.isValid()){
        checkHandleMethod(option->m_preMethod);
    }
    if(option->m_postMethod.isValid()){
        checkHandleMethod(option->m_postMethod);
    }
}

void ICmdWare::checkArgsMethod()
{
    if(m_args == nullptr){
        return;
    }
    QString position = QString(" [Class]: ").append(m_className).append(" [Args Name]: ").append(m_args->m_name);

    if(!m_args->m_prop.isValid()){
        throw ICmdException("Action Args property is not exist. " + position);
    }

    if(!m_args->m_method.isValid()){
        throw ICmdException("Action Args $set_value_xxx method not valid. " + position);
    }

    if(m_args->m_postMethod.isValid()){
        checkHandleMethod(m_args->m_postMethod);
    }
    if(m_args->m_preMethod.isValid()){
        checkHandleMethod(m_args->m_preMethod);
    }
}

void ICmdWare::checkArgxMethod(ICmdArgx *argx)
{
    QString position = QString(" [Class]: ").append(m_className)
            .append(" [argx name]: ").append(argx->m_name)
            .append(" [argx index]: ").append(QString::number(argx->m_index));
    if(!argx->m_method.isValid()){
        throw ICmdException("argx $set_value_xxx method is not valid. " + position);
    }

    if(argx->m_postMethod.isValid()){
        checkHandleMethod(argx->m_postMethod);
    }
    if(argx->m_preMethod.isValid()){
        checkHandleMethod(argx->m_preMethod);
    }
}

void ICmdWare::checkOptionShortNameComflict()
{
    QString position = QString(" [Class]: ").append(m_className);
    QStringList names;
    for(auto option : m_optionValues){
        if(!option->m_shortName.isEmpty()){
            if(names.contains(option->m_shortName)){
                throw ICmdException("Options shortname conflicted. " + QString(" [short name]: ").append(option->m_shortName) + position);
            }
            names.append(option->m_shortName);
        }
    }
}

void ICmdWare::checkHandleMethod(const QMetaMethod &method)
{
    QString position = QString(" [Class]: ").append(m_className);
    if(method.returnType() != QMetaType::Void){
        throw ICmdException("PreHandle or PostHandle function return type must be void" + QString(" [Function Name]: ").append(method.methodSignature()) + position);
    }

    if(method.parameterCount()> 1){
        throw ICmdException("PreHandle or PostHandle function argument count must be one or zero" + QString(" [Function Name]: ").append(method.methodSignature()) + position);
    }

    if(method.parameterCount() == 1){
        auto names = getMethodArguments(method);
        if(names.first() != "ICmdRequest" || names.first() != "ICmdRequest&" ){
            throw ICmdException("PreHandle or PostHandle function arguments type can only be ICmdRequest. " + position);
        }
        throw ICmdException("PreHandle or PostHandle function argument type can only be ICmdRequest." + QString(" [Function Name]: ").append(method.methodSignature()) + position);
    }
}

QStringList ICmdWare::getMethodArguments(const QMetaMethod &method)
{
    QStringList names;
    for(auto name : method.parameterTypes()){
        names.append(name);
    }
    return names;
}

$PackageWebCoreEnd
