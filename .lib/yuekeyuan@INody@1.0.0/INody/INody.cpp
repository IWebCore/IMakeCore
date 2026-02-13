#include "INody.h"
#include "INodyManage.h"
#include "INodyParser.h"

$PackageWebCoreBegin

INody *INody::clone()
{
    if(auto ptr = dynamic_cast<INodyWithChild*>(this)){
        ptr->m_child = ptr->m_child->clone();
    }
    if(auto ptr = dynamic_cast<INodyWithChildren*>(this)){
        auto children = ptr->m_children;
        ptr->m_children.clear();
        for(auto child : children){
            ptr->m_children.append(child->clone());
        }
    }
    if(auto ptr = dynamic_cast<INodyWithTwins*>(this)){
        ptr->m_elder = ptr->m_elder->clone();
        ptr->m_younger = ptr->m_younger->clone();
    }
    return this;
}

IJson INody::getValue(IStringView path, const IJson &global, const QList<const IJson*>& context)
{
    std::string path_str(path);
    IJson::json_pointer p(path_str);

    for(auto c : context){
        if(c->contains(p)){
            return (*c)[p];
        }
    }

    if(global.contains(p)){
        return global[p];
    }
    return nullptr;
}

INodyWithChildren::~INodyWithChildren()
{
    for(auto node : m_children){
        delete node;
    }
}

INodyWithChild::~INodyWithChild()
{
    delete m_child;
}

INodyWithTwins::~INodyWithTwins()
{
    delete m_elder;
    delete m_younger;
}

std::string IContentNody::execute(const IJson& root, const QList<const IJson*>& context)
{
    return m_child->execute(root, context);
}

std::string IUnionNody::execute(const IJson& root, const QList<const IJson*>& context)
{
    std::string ret;
    for(auto node : m_children){
        ret += node->execute(root, context);
    }
    return ret;
}

std::string IHtmlNody::execute(const IJson&, const QList<const IJson*>&)
{
    return m_html.toStdString();
}

std::string IVariableNody::execute(const IJson& root, const QList<const IJson*>& context)
{
    auto value = getValue(m_path, root, context);
    if(value.is_null()){
        return {};
    }else if(value.is_string()){
        return value.get<std::string>();
    }if(value.is_boolean()){
        return value.get<bool>() ? "true" : "false";
    }else if(value.is_number_float()){
        return std::to_string(value.get<double>());
    }else if(value.is_number_unsigned()){
        return std::to_string(value.get<std::uint64_t>());
    }else if(value.is_number_integer()){
        return std::to_string(value.get<std::int64_t>());
    }else if(value.is_array()){
        return value.dump();
    }else if(value.is_object()){
        return value.dump();
    }
    return {};
}

// NOTE: bool 类型转换问题
std::string IfNody::execute(const IJson& root, const QList<const IJson*>& context)
{
    auto value = getValue(m_path, root, context);
    bool condition{false};
    if(value.is_null()){
        condition = false;
    }else if(value.is_boolean()){
        condition = value.get<bool>();
    }else if(value.is_string()){
        std::string res = value.get<std::string>();
        condition = !res.empty();
    }else if(value.is_number()){
        condition = value.get<double>() != 0;
    }else if(value.is_array()){
        condition = !value.empty();
    }else if(value.is_object()){
        condition = !value.empty();
    }else{
        condition = false;
    }

    if(condition){
        if(m_elder){
            return m_elder->execute(root, context);
        }
    }else{
        if(m_younger){
            return m_younger->execute(root, context);
        }
    }
    return {};
}

std::string IForNody::execute(const IJson& root, const QList<const IJson*>& context)
{
    std::string ret;
    IJson value = getValue(m_path, root, context);
    if(value.is_array()){
        IJson::json_pointer path(m_var.toStdString());

        IJson json;
        auto forContext = context;
        forContext.prepend(&json);

        for(const auto& var : value){
            json[path] = var;
            ret += m_child->execute(root, forContext);
        }
    }
    return ret;
}

std::string IWithNody::execute(const IJson& root, const QList<const IJson*>& context)
{
    auto value = getValue(m_var, root, context);
    if(value.is_null()){
        return m_child->execute(root, context);
    }

    auto withContext = context;
    IJson json;
    withContext.prepend(&json);

    json[IJson::json_pointer(m_path.toStdString())]= value;
    return m_child->execute(root, withContext);
}

std::string IIncludeNody::execute(const IJson& root, const QList<const IJson*>& context)
{
    if(m_child){
        return m_child->execute(root, context);
    }
    return {};
}

void IIncludeNody::computeNody(INodyParser* parser)
{
    m_child = parser->parseFile(m_path);
    if(m_child == nullptr){
        qFatal("file not found");
    }
}

std::string IBlockNody::execute(const IJson& root, const QList<const IJson*>& context)
{
    if(m_child){
        return m_child->execute(root, context);
    }
    return {};
}

std::string ISlotNody::execute(const IJson& root, const QList<const IJson*>& context)
{
    if(m_child){
        return m_child->execute(root, context);
    }
    return {};
}

std::string IExtendNody::execute(const IJson& root, const QList<const IJson*>& context)
{
    if(m_child){
        return m_child->execute(root, context);
    }
    return {};
}

void IExtendNody::computeNody(INodyParser* parser)
{
    m_child = parser->parseFile(m_path);
    QMap<IString, IBlockNody* > map;
    for(auto node : m_children){
        map[dynamic_cast<IBlockNody*>(node)->m_name] = dynamic_cast<IBlockNody*>(node);
    }

    replaceBlock(m_child, map);
}

void IExtendNody::replaceBlock(INody *node, const QMap<IString, IBlockNody *>& map)
{
    if(auto ptr = dynamic_cast<INodyWithChild*>(node)){
        if(auto child = dynamic_cast<ISlotNody*>(ptr->m_child)){
            if(map.contains(child->m_name.toStdString())){
                ptr->m_child = map[child->m_name]->clone();
                delete child;
            }
        }else{
            replaceBlock(ptr->m_child, map);
        }
    }

    if(auto ptr = dynamic_cast<INodyWithTwins*>(node)){
        if(auto child = dynamic_cast<ISlotNody*>(ptr->m_elder)){
            if(map.contains(child->m_name.toStdString())){
                ptr->m_elder = map[child->m_name]->clone();
                delete child;
            }
        }else{
            replaceBlock(ptr->m_elder, map);
        }

        if(auto child = dynamic_cast<ISlotNody*>(ptr->m_younger)){
            if(map.contains(child->m_name.toStdString())){
                ptr->m_younger = map[child->m_name]->clone();
                delete child;
            }
        }else{
            replaceBlock(ptr->m_younger, map);
        }
    }

    if(auto ptr = dynamic_cast<INodyWithChildren*>(node)){
        int len = ptr->m_children.length();
        for(auto i=0; i<len; i++){
            if(auto child = dynamic_cast<ISlotNody*>(ptr->m_children[i])){
                if(map.contains(child->m_name.toStdString())){
                    ptr->m_children[i] = map[child->m_name]->clone();
                    delete child;
                }
            }else{
                replaceBlock(ptr->m_children[i], map);
            }
        }
    }
}

std::string IFunNody::execute(const IJson& root, const QList<const IJson*>& context)
{
    Q_UNUSED(root)
    Q_UNUSED(context)
    return {};
}


$PackageWebCoreEnd
