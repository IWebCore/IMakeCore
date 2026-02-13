#include "INodyManage.h"
#include "INodyResolverWare.h"

$PackageWebCoreBegin

void INodyManage::registNodyResolverWare(INodyResolverWare *ware)
{
    m_wares.push_back(ware);
}

bool INodyManage::canParse(const IString &path)
{
    for(auto ware : m_wares){
        if(ware->match(path)){
            return true;
        }
    }
    return false;
}

std::string INodyManage::parse(const IString &path, const IJson &object)
{
    for(auto ware : m_wares){
        if(ware->match(path)){
            return ware->parse(path, object);
        }
    }

    return {};  // do not match
}

$PackageWebCoreEnd
