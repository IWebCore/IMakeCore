#pragma once

#include "IApplicationWare.h"
#include "IApplicationManage.h"
#include "core/task/unit/ITaskInstantUnit.h"
#include "core/unit/ISoloUnit.h"

template<typename T, bool enabled=true>
class IApplicationInterface : public IApplicationWare, public ITaskInstantUnit<T, true>, public ISoloUnit<T>
{
public:
    IApplicationInterface();

public:
    virtual std::int64_t time() final;

private:
    virtual void $task() override;

protected:
    inline static std::atomic_int64_t m_time = std::chrono::duration_cast<std::chrono::nanoseconds>(std::chrono::high_resolution_clock().now().time_since_epoch()).count();;
};

template<typename T, bool enabled>
IApplicationInterface<T, enabled>::IApplicationInterface()
{
    // m_time =
}

template<typename T, bool enabled>
int64_t IApplicationInterface<T, enabled>::time()
{
    return ++m_time;
}

template<typename T, bool enabled>
void IApplicationInterface<T, enabled>::$task()
{
    IApplicationManage::instance().registerAppFuns(applicationType(), [&](int argc, char** argv) -> IApplicationWare*{
        return invoke(argc, argv);
    });
}
