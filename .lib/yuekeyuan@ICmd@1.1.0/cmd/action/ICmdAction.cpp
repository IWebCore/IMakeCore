#include "ICmdAction.h"
#include "core/application/iApp.h"
#include "core/application/IApplicationManage.h"
#include "cmd/ICmdRequest.h"
#include "cmd/ICmdException.h"
#include "cmd/action/ICmdOptionValue.h"
#include "cmd/action/ICmdOption.h"
#include "cmd/action/ICmdArgs.h"
#include "cmd/action/ICmdArgx.h"

$PackageWebCoreBegin

ICmdAction::ICmdAction()
{
}

bool ICmdAction::isMatch(const ICmdRequest &request)
{
    if(request.m_paths == m_paths){
        return true;
    }
    return false;
}

void ICmdAction::execute(const ICmdRequest &request)
{
    checkOptionValues(request);
    checkOptionOns(request);

    executeOptions(request);
    executeOptionOns(request);
    executeArgs(request);
    executeArgx(request);
    executeMain(request);
}

void ICmdAction::printHelp()
{
    printBasic();
    printOptions();
    printOptionValues();
    printArgs();
    printArgx();
}

void ICmdAction::executeOptions(const ICmdRequest &request)
{
    for(auto option : m_optionValues){
        try{
            option->execute(*this, request);
        }catch(const ICmdException& e){
            QString tip = e.getCause();
            qDebug().noquote().nospace()
                    << "ERROR OCCURED: " << tip << " [Cmd Path]: " << request.m_paths.join(" ")
                     << " [Cmd Arg Type]: Option"
                     << " [Cmd Option Name]: " << option->m_name << Qt::endl;
            printHelp();
            exit(1);
        }
    }
}

void ICmdAction::checkOptionValues(const ICmdRequest &request)
{
    // request -> definition
    // 这种情况是检查 request option 给了参数，但是 optionValue 没有定义的情况
    for(const QString& key : request.m_options.keys()){
        if(request.m_options[key].isEmpty()){
            continue;
        }
        bool ok = false;
        if(key.startsWith("--")){
            QString newKey = key.mid(2);
            for(auto val : m_optionValues){
                if(val->m_name == newKey){
                    ok = true;
                    break;
                }
            }
        }else{
            QString newKey = key.mid(1);
            for(auto val : m_optionValues){
                if(val->m_shortName == newKey){
                    ok = true;
                    break;
                }
            }
        }

        if(!ok){
            QString tip = "your input option value are not defined in this cmd. [Option]: " + key;
            qDebug().noquote().nospace() << "ERROR OCCURED: " << tip << " [Cmd Path]: " << request.m_paths.join(" ");
            printHelp();
            exit(1);
        }
    }

    // definition -> request
    // 这个是检查定义了 optionValue,并且optionValue 不能为空的情况， 而请求中没有给值
    for(auto val : m_optionValues){
        if(val->m_nullable){
            continue;
        }
        bool ok{false};
        QString fullName = "--" + val->m_name;
        if(request.m_options.contains(fullName) && !request.m_options[fullName].isEmpty()){
            ok = true;
        }
        QString shortName = "-" + val->m_shortName;
        if(!val->m_shortName.isEmpty() && request.m_options.contains(shortName) && ! request.m_options[shortName].isEmpty()){
            ok = true;
        }
        if(!ok){
            qDebug().noquote().nospace() << "cmd defined option value and option value should not be null, but you do not provide option value. "
                     << "[OptionValue]:" << val->m_name;

            printHelp();
            exit(1);
        }
    }
}

void ICmdAction::checkOptionOns(const ICmdRequest &request)
{
    // request -> definition
    for(const QString& key : request.m_options.keys()){
        bool ok = false;
        if(key.startsWith("--")){
            QString newKey = key.mid(2);
            for(auto val : m_options){
                if(val->m_name == newKey){
                    ok = true;
                    break;
                }
            }
        }else{
            QString newKey = key.mid(1);
            for(auto val : m_options){
                if(val->m_shortName == newKey){
                    ok = true;
                    break;
                }
            }
        }

        if(!ok){
            QString tip = "your input options are not defined in this cmd. [Option]: " + key;
            qDebug().noquote().nospace()
                    << "ERROR OCCURED: " << tip << " [Cmd Path]: " << request.m_paths.join(" ");
            printHelp();
            exit(1);
        }
    }

    //definition -> request
    for(auto val : m_options){
        if(val->m_isRequired){
            bool ok = false;
            auto fullName = "--" + val->m_name;
            if(request.m_options.contains(fullName) && !request.m_options.value(fullName).isEmpty()){
                ok = true;
            }
            auto shortName = "-" + val->m_shortName;
            if(request.m_options.contains(shortName) && !request.m_options.value(shortName).isEmpty()){
                ok = true;
            }
            if(!ok){
                qDebug().noquote().nospace() << "your cmds do not contain options "
                                             << val->m_name
                                             << " which is required";
                printHelp();
                exit(1);
            }
        }
    }
}

void ICmdAction::executeOptionOns(const ICmdRequest &request)
{
    for(auto on : m_options){
        try{
            on->execute(*this, request);
        }catch(const ICmdException& e){
            QString tip = e.getCause();
            qDebug().noquote().nospace()
                    << "ERROR OCCURED: " << tip << " [Cmd Path]: " << request.m_paths.join(" ")
                     << " [Cmd Arg Type]: OptionON"
                     << " [Cmd Option ON Name]: " << on->m_name << Qt::endl;

            printHelp();
            exit(1);
        }
    }
}

void ICmdAction::executeArgs(const ICmdRequest &request)
{
    if(m_args){
        try{
            m_args->execute(*this, request);
        }catch(const ICmdException& e){
            QString tip = e.getCause();
            qDebug().noquote().nospace()
                    << "ERROR OCCURED: " << tip << " [Cmd Path]: " << request.m_paths.join(" ")
                     << " [Cmd Arg Type]: Args"
                     << " [Cmd Arg Values]: " << request.m_arguments.join(", ") << Qt::endl;

            printHelp();
            exit(1);
        }
    }
}

void ICmdAction::executeArgx(const ICmdRequest &request)
{
    for(auto argx : m_argxes){
        try{
           argx->execute(*this, request);
        } catch(const ICmdException& e){
            QString tip = e.getCause();
            qDebug().noquote().nospace()
                    << "ERROR OCCURED: " << tip << " [Cmd Path]: " << request.m_paths.join(" ")
                     << " [Cmd Arg Type]: ArgX" << " [ArgX Name]: " << argx->m_name
                     << " [ArgX Index]: " << QString::number(argx->m_index) << Qt::endl;

            printHelp();
            exit(1);
        }
    }
}

void ICmdAction::executeMain(const ICmdRequest& request)
{
    ParamType params{0};
    params[0] = QMetaType(QMetaType::Void).create();
    params[1] = const_cast<ICmdRequest*>(&request);

    auto index = m_method.methodIndex();
    auto obj = static_cast<QObject*>(m_ptr);
    m_callable(obj, QMetaObject::InvokeMetaMethod, index, params.data());

    QMetaType(QMetaType::Void).destroy(params[0]);
}

void ICmdAction::printBasic()
{
    qDebug().noquote().nospace() << "[CMD]:";
    qDebug().noquote().nospace() << "    " << iApp->applicationName() << " " << m_paths.join(" ");
    if(!m_memo.isEmpty()){
        qDebug().noquote().nospace() << "[Memo]:";
        qDebug().noquote().nospace() << "    " << m_memo;
    }
}

void ICmdAction::printOptions()
{
    if(m_options.isEmpty()){
        return;
    }

    qDebug().noquote().nospace() << "[Options]:";

    int fullLength{6}, shortLength{9}, requriedLength{10}, noValueLength{9};
    for(auto opt : m_options){
        fullLength = std::max({static_cast<int>(opt->m_name.length()) + 2, fullLength});
        shortLength = std::max({static_cast<int>(opt->m_shortName.length()) + 1, shortLength});
    }
    qDebug().noquote().nospace()
            << "    "
            << qSetFieldWidth(fullLength + 2) << Qt::left << "Option"
            << qSetFieldWidth(shortLength + 2) << Qt::left << "ShortName"
            << qSetFieldWidth(requriedLength +2) << Qt::left << "Required"
            << qSetFieldWidth(noValueLength + 2) << Qt::left << "NoValue"
            << "Memo";


    for(auto opt : m_options){
        qDebug().noquote().nospace()
                << "    "
                << qSetFieldWidth(fullLength + 2) << Qt::left << "--" + opt->m_name
                << qSetFieldWidth(shortLength + 2) << Qt::left << "-" + opt->m_shortName
                << qSetFieldWidth(requriedLength +2) << Qt::left << opt->m_isRequired
                << qSetFieldWidth(noValueLength + 2) << Qt::left << opt->m_isNoValue
                << opt->m_memo;
    }

}

void ICmdAction::printOptionValues()
{
    if(m_optionValues.isEmpty()){
        return;
    }
    int optNameLength = 6;
    int nameLength = 4;
    int typeNameLength = 8;
    int nullableLength = 8;

    for(const ICmdOptionValue* val : m_optionValues){
        optNameLength = std::max({optNameLength, static_cast<int>(val->m_name.length())});
        nameLength = std::max({nameLength, static_cast<int>(val->m_valueName.length())});
        typeNameLength = std::max({typeNameLength, static_cast<int>(QString(val->m_prop.typeName()).length())});
    }

    qDebug().noquote().nospace() << "[OptionValues]:";
    qDebug().noquote().nospace() << "    "
                                 << qSetFieldWidth(optNameLength + 2) << Qt::left << "Option"
                                 << qSetFieldWidth(nameLength + 2) << Qt::left << "Name"
                                 << qSetFieldWidth(typeNameLength + 2) << Qt::left << "TypeName"
                                 << qSetFieldWidth(nullableLength + 2) << Qt::left << "Nullable"
                                 << "Memo";

    for(const ICmdOptionValue* val : m_optionValues){

        qDebug().noquote().nospace() << "    "
                                     << qSetFieldWidth(optNameLength + 2) << Qt::left << val->m_name
                                     << qSetFieldWidth(nameLength + 2) << Qt::left << val->m_valueName
                                     << qSetFieldWidth(typeNameLength + 2) << Qt::left << val->m_prop.typeName()
                                     << qSetFieldWidth(nullableLength + 2) << Qt::left << val->m_nullable
                                     << val->m_memo;
    }
}

void ICmdAction::printArgs()
{
    if(m_args == nullptr){
        return;
    }

    qDebug().noquote().nospace() << "[Args]:";

    int nameLength = std::max({static_cast<int>(m_args->m_name.length()), 4}) + 2;
    int typeNameLength = std::max({8, static_cast<int>(QString(m_args->m_prop.typeName()).length())}) + 2;
    qDebug().noquote().nospace()
            << "    "
            << qSetFieldWidth(nameLength) << Qt::left << "Name"
            << qSetFieldWidth(typeNameLength) << "TypeName"
            << qSetFieldWidth(10) << Qt::left << "Nullable"
            << "Memo";

    qDebug().noquote().nospace()
            << "    "
            << qSetFieldWidth(nameLength) << Qt::left << m_args->m_name
            << qSetFieldWidth(typeNameLength) << m_args->m_prop.typeName()
            << qSetFieldWidth(10) << Qt::left << m_args->m_nullable
            << m_args->m_memo;
}

void ICmdAction::printArgx()
{
    if(m_argxes.empty()){
        return;
    }

    int nameLength = 4;
    int typeNameLength = 8;

    for(const auto& argx : m_argxes){
        nameLength = std::max({nameLength, static_cast<int>(argx->m_name.length())});
        typeNameLength = std::max({typeNameLength, static_cast<int>(QString(argx->m_property.typeName()).length())});
    }

    qDebug().noquote().nospace() << "[Argx]:";


    qDebug().noquote().nospace()
            << "    "
            << qSetFieldWidth(7) << Qt::left << "Index"
            << qSetFieldWidth(nameLength+2) << Qt::left << "Name"
            << qSetFieldWidth(typeNameLength + 2) << Qt::left << "TypeName"
            << qSetFieldWidth(10) << Qt::left << "Nullable"
            << "Memo";


    for(const auto& argx : m_argxes){
        qDebug().noquote().nospace()
                << "    "
                << qSetFieldWidth(7) << Qt::left << argx->m_index
                << qSetFieldWidth(nameLength+2) << Qt::left << argx->m_name
                << qSetFieldWidth(typeNameLength + 2) << Qt::left << argx->m_property.typeName()
                << qSetFieldWidth(10) << Qt::left << argx->m_nullable
                << argx->m_memo;
    }
}

$PackageWebCoreEnd
