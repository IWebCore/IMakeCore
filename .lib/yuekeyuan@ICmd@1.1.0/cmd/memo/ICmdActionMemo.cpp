#include "ICmdActionMemo.h"
#include "cmd/action/ICmdOptionValue.h"
#include "cmd/action/ICmdOption.h"
#include "cmd/action/ICmdArgx.h"
#include "cmd/action/ICmdArgs.h"

$PackageWebCoreBegin

ICmdActionMemo::ICmdActionMemo(const ICmdAction *action)
{
    m_path = action->m_paths;
    m_memo = action->m_memo;

    for(auto option : action->m_optionValues){
        m_optionMemo.append(createOptionMemo(option, action));
    }
}

ICmdActionOptionMemo ICmdActionMemo::createOptionMemo(const ICmdOptionValue *opt, const ICmdAction *act)
{
    ICmdActionOptionMemo memo;
    memo.m_name = opt->m_name;
    memo.m_shortName = opt->m_shortName;
    memo.m_memo = opt->m_memo;

    // 处理另外一处 memo 验证
    if(!memo.m_isRequired){
        for(auto on : act->m_options){
            if(on->m_name == memo.m_name){
                memo.m_isRequired = on->m_isRequired;
            }
        }
    }

    return memo;
}

$PackageWebCoreEnd
