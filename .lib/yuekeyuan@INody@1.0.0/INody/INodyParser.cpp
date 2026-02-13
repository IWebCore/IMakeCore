#include "INodyParser.h"
#include "INodyException.h"

#include "core/util/IFileUtil.h"
#include <regex>

$PackageWebCoreBegin


QMap<IStringView, INodyParser::Fun> INodyParser::s_map;
IStringViewList INodyParser::s_keys;

namespace detail
{
IStringView extract_variable_name(IStringView input)
{
    size_t start = 0, end = 0;
    while (end < input.size()) {
        const char c = input[end];
        if (!std::isalnum(static_cast<unsigned char>(c)) && c != '/' && c!= '_' && c != '-') {
            break;
        }
        end++;
    }
    return (start < end) ? input.substr(start, end - start) : IStringView{};
}

IStringView extract_file_name(IStringView input)
{
    size_t start = 0, end = 0;
    while (end < input.size()) {
        const char c = input[end];
        if (!std::isalnum(static_cast<unsigned char>(c)) && c != '.' && c!= '_' && c != '-') {
            break;
        }
        end++;
    }
    return (start < end) ? input.substr(start, end - start) : IStringView{};
}

}

INodyParser::INodyParser(const IString& wd)
{
    setWorkingDirectory(wd);
    static std::once_flag flag;
    std::call_once(flag, [&](){
        s_map = QMap<IStringView, INodyParser::Fun>{
            {"$if ", &INodyParser::parseIf},
            {"$for ", &INodyParser::parseFor},
            {"${{", &INodyParser::parseVar},
            {"#{{", &INodyParser::parseComment},
            {"$block ", &INodyParser::parseBlock},
            {"$slot", &INodyParser::parseSlot},
            {"$include", &INodyParser::parseInclude},
            {"$with ", &INodyParser::parseWith}
        };
        s_keys = s_map.keys();
    });
}

// 返回空指针意味着parse 失败
void INodyParser::setWorkingDirectory(const IString &directory)
{
    m_wd = directory;
}

INody* INodyParser::parse(IStringView view)
{
    auto head = new IContentNody;
    head->m_content = view;
    head->m_content.solidify();
    IStringView content = head->m_content;

    try{
        if(content.trimmed().startWith("$extend")){
            content = eatVariable(content, "$extend", "$extend has no prefix");
            std::tie(head->m_child, content) = parseExtend(content);
        }else{
            std::tie(head->m_child, content) = parseMixed(content);
        }

        if(!content.empty()){
            throw INodyException("parse file", content);
        }

    }catch(const INodyException& e){
        delete head;
        qDebug().noquote() << e.what() << "\n\tIN CONTENT: "<< view.toQString();
        return nullptr;
    }
    return head;
}

INody *INodyParser::parseFile(IString path)
{
    auto realPath = m_wd.toQString().append("/").append(path.toQString());
    auto content = IFileUtil::readFileAsString(realPath);
    if(content){
        return parse(IStringView(content.value().toStdString()));
    }
    return nullptr;
}

std::pair<INody*, IStringView> INodyParser::parseMixed(IStringView content)
{
    QList<INody*> nodes;
    INody* node{};

    while(!content.empty() && !content.startWith("}}")){
        content = content.trimmed();
        for(const auto& key : s_keys){
            if(content.startWith(key)){
                content = content.substr(key.length()).trimmed();
                std::tie(node, content) = std::mem_fn(s_map[key])(this, content);
                if(node){
                    nodes.append(node);
                }
                break;
            }
        }

        std::tie(node, content) = parseHtml(content);
        if(node){
            nodes.append(node);
        }
    }

    if(nodes.isEmpty()){
        return {nullptr, content};
    }
    if(nodes.length() == 1){
        return {nodes.first(), content};
    }

    auto unionNode = new IUnionNody;
    unionNode->m_children = nodes;
    return {unionNode, content};
}

std::pair<INody*, IStringView> INodyParser::parseHtml(IStringView content)
{
    static const char* EndTag = "}}";
    IStringViewList tags = s_keys;
    tags.append(EndTag);

    std::size_t index = content.length();
    for(auto tag : tags){
        auto pos = content.find(tag);
        if(pos != std::string::npos){
            index = index < pos ? index : pos;
        }
    }

    auto node = new IHtmlNody;
    node->m_html = content.substr(0, index);
    return {node, content.substr(index)};
}

std::pair<INody*, IStringView> INodyParser::parseIf(IStringView content)
{
    auto ifNode = new IfNody;
    std::tie(ifNode->m_path, content) = readVariable(content, "$if statement can not read condition");
    content = eatBeginVariable(content, "$if");

    std::tie(ifNode->m_elder, content) = parseMixed(content);
    content = eatEndVariable(content, "$if");

    if(content.startWith("$elif ")){
        content = content.substr(std::string("$elif ").size()).trimmed();
        std::tie(ifNode->m_younger, content) = parseElif(content);
    }else if(content.startWith("$else")){
        content = content.substr(std::string("$else").size()).trimmed();
        std::tie(ifNode->m_younger, content) = parseElse(content);
    }

    return {ifNode, content};
}

std::pair<INody*, IStringView> INodyParser::parseElif(IStringView content)
{
    auto ifNode = new IfNody;
    std::tie(ifNode->m_path, content) = readVariable(content, "$elif statement can not read condition");
    content = eatBeginVariable(content, "$elif");
    std::tie(ifNode->m_elder, content) = parseMixed(content);
    content = eatEndVariable(content, "$elif");

    if(content.startWith("$elif ")){
        std::tie(ifNode->m_younger, content) = parseElif(content.substr(std::string("$elif ").size()));
    }else if(content.startWith("$else")){
        std::tie(ifNode->m_younger, content) = parseElse(content.substr(std::string("$else").size()));
    }

    return {ifNode, content.trimmed()};
}

std::pair<INody*, IStringView> INodyParser::parseElse(IStringView content)
{
    INody* node{};
    content = eatBeginVariable(content, "$else");
    std::tie(node, content) = parseMixed(content);
    content = eatEndVariable(content, "$else");
    return {node, content.trimmed()};
}

std::pair<INody*, IStringView> INodyParser::parseFor(IStringView content)
{
    auto forNode = new IForNody();
    std::tie(forNode->m_var, content) = readVariable(content, "$for statement can not read loop iterator");
    content = eatVariable(content, "in", "$for has no in");

    std::tie(forNode->m_path, content) = readVariable(content, "$for statement can not read loop body");
    content = eatBeginVariable(content, "$for");

    std::tie(forNode->m_child, content) = parseMixed(content);
    content = eatEndVariable(content, "$for");

    return {forNode, content.trimmed()};
}

// ?
std::pair<INody*, IStringView> INodyParser::parseVar(IStringView content)
{
    auto varNode = new IVariableNody();
    std::tie(varNode->m_path, content) = readVariable(content, "${{ statement can not read path");
    content = eatEndVariable(content, "variable");
    return {varNode, content.trimmed()};
}

std::pair<INody*, IStringView> INodyParser::parseComment(IStringView content)
{
    INody* node{};
    std::tie(node, content) = parseMixed(content);
    delete node;

    content = eatEndVariable(content, "#{{");
    return {nullptr, content.trimmed()};
}

std::pair<INody*, IStringView> INodyParser::parseExtend(IStringView content)
{
    auto extendNode = new IExtendNody;
    content = eatBeginVariable(content, "$extend");
    std::tie(extendNode->m_path, content) = readFileName(content, "$extend fail to read path");
    content = eatEndVariable(content, "$extend");

    while(content.startWith("$block ")){
        INody* blockNode{};
        std::tie(blockNode, content) = parseBlock(content.substr(std::string("$block ").size()));
        extendNode->m_children.append(dynamic_cast<IBlockNody*>(blockNode));
    }
    extendNode->computeNody(this);

    return {extendNode, content};
}

std::pair<INody*, IStringView> INodyParser::parseBlock(IStringView content)
{
    auto node = new IBlockNody;
    std::tie(node->m_name, content) = readVariable(content, "$block statement can not read block name");
    content = eatBeginVariable(content, "$block");
    std::tie(node->m_child, content) = parseMixed(content);
    content = eatEndVariable(content, "$block");
    return {node, content};
}

std::pair<INody *, IStringView> INodyParser::parseSlot(IStringView content)
{
    auto node = new ISlotNody();
    content = eatBeginVariable(content,"$include");
    std::tie(node->m_name, content) = readVariable(content, "$slot error with read variable");
    content = eatEndVariable(content, "$include");
    node->computeNody(this);
    return {node, content.trimmed()};
}

std::pair<INody*, IStringView> INodyParser::parseInclude(IStringView content)
{
    auto node = new IIncludeNody();
    content = eatBeginVariable(content,"$include");
    std::tie(node->m_path, content) = readFileName(content, "$include error with read variable");
    content = eatEndVariable(content, "$include");
    node->computeNody(this);
    return {node, content.trimmed()};
}

std::pair<INody*, IStringView> INodyParser::parseWith(IStringView content)
{
    auto node = new IWithNody;
    std::tie(node->m_var, content) = readVariable(content, "$with fail read var");
    content = eatVariable(content, "as ", "$with has no as");
    std::tie(node->m_path, content) = readVariable(content, "$with fail read path");
    content = eatBeginVariable(content, "$with");
    std::tie(node->m_child, content) = parseMixed(content);
    content = eatEndVariable(content, "$with");
    return {node, content};
}

std::pair<INody*, IStringView> INodyParser::parseFunction(IStringView content)
{
    auto nody = new IFunNody;
    std::tie(nody->m_funName, content) = readVariable(content, "$fun error with function");
    content = eatBeginVariable(content, "$fun");
    std::tie(nody->m_child, content) = parseMixed(content);
    content = eatEndVariable(content, "$fun");
    return {nody, content.trimmed()};
}

std::pair<IString, IStringView> INodyParser::readVariable(IStringView content, const IString& failReason)
{
    content = content.trimmed();
    auto variable = detail::extract_variable_name(content);
    if(variable.empty()){
        throw INodyException(failReason, content);
        return {};
    }
    return {variable, content.substr(variable.length())};
}

std::pair<IString, IStringView> INodyParser::readFileName(IStringView content, const IString &failReason)
{
    content = content.trimmed();
    auto variable = detail::extract_file_name(content);
    if(variable.empty()){
        throw INodyException(failReason, content.toQString());
        return {};
    }
    return {variable, content.substr(variable.length())};
}

IStringView INodyParser::eatVariable(IStringView content, IStringView val, const IString &failReason)
{
    content = content.trimmed();
    if(!content.startWith(val)){
        throw INodyException(failReason.toQString() + " variable:"+  val.toQString(), content.toQString());
    }
    return content.substr(val.length()).trimmed();
}

IStringView INodyParser::eatBeginVariable(IStringView content, const IString &failReason)
{
    return eatVariable(content.trimmed(), "{{", failReason.toQString() + " has no start tag: {{");
}

IStringView INodyParser::eatEndVariable(IStringView content, const IString &failReason)
{
    return eatVariable(content.trimmed(), "}}", failReason.toQString() + " has no end tag: }}");
}


$PackageWebCoreEnd
