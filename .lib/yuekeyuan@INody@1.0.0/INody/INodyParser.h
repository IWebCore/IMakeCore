#pragma once

#include "core/util/IHeaderUtil.h"
#include "INody.h"

$PackageWebCoreBegin


class INodyParser
{
private:
    using Fun = std::pair<INody*, IStringView> (INodyParser::*)(IStringView);

public:
    INodyParser(const IString& directory);
    void setWorkingDirectory(const IString& directory);

public:
    INody* parse(IStringView content);
    INody* parseFile(IString path);

private:
    std::pair<INody*, IStringView> parseMixed(IStringView);
    std::pair<INody*, IStringView> parseHtml(IStringView);
    std::pair<INody*, IStringView> parseIf(IStringView content);
    std::pair<INody*, IStringView> parseElif(IStringView content);
    std::pair<INody*, IStringView> parseElse(IStringView content);
    std::pair<INody*, IStringView> parseFor(IStringView content);
    std::pair<INody*, IStringView> parseVar(IStringView content);
    std::pair<INody*, IStringView> parseComment(IStringView content);
    std::pair<INody*, IStringView> parseExtend(IStringView content);
    std::pair<INody*, IStringView> parseBlock(IStringView content);
    std::pair<INody*, IStringView> parseSlot(IStringView content);
    std::pair<INody*, IStringView> parseInclude(IStringView content);
    std::pair<INody*, IStringView> parseWith(IStringView content);
    std::pair<INody*, IStringView> parseFunction(IStringView content);    // $fun name {{}}

private:
    std::pair<IString, IStringView> readVariable(IStringView content, const IString& failReason);
    std::pair<IString, IStringView> readFileName(IStringView content, const IString& failReason);
    IStringView eatVariable(IStringView content, IStringView val, const IString& failReason);
    IStringView eatBeginVariable(IStringView content, const IString& failReason);
    IStringView eatEndVariable(IStringView content, const IString&failReason);

private:
    static QMap<IStringView,  Fun> s_map;
    static IStringViewList s_keys;

private:
    IString m_wd;
};


$PackageWebCoreEnd
