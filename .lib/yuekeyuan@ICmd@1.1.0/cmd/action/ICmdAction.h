#pragma once

#include "core/util/IHeaderUtil.h"
#include "core/unit/IGadgetUnit.h"

$PackageWebCoreBegin

class ICmdRequest;
class ICmdArgs;
class ICmdArgx;
class ICmdOptionValue;
class ICmdOption;
class ICmdAction
{
private:
    using ParamType = std::array<void*, 11>;

public:
    ICmdAction();

public:
    bool isMatch(const ICmdRequest&);
    void execute(const ICmdRequest& request);

public:
    void printHelp();

private:
    void executeOptions(const ICmdRequest& request);
    void checkOptionValues(const ICmdRequest& request);
    void checkOptionOns(const ICmdRequest& request);
    void executeOptionOns(const ICmdRequest& request);
    void executeArgs(const ICmdRequest& request);
    void executeArgx(const ICmdRequest& request);
    void executeMain(const ICmdRequest& request);

private:
    void printBasic();
    void printOptions();
    void printOptionValues();
    void printArgs();
    void printArgx();

public:
    void* m_ptr{};
    QString m_memo;
    QStringList m_paths;
    QMetaMethod m_method{};
    IGadgetUnit::StaticMetacallFunction m_callable;

    ICmdArgs* m_args{nullptr};
    QList<ICmdOptionValue*> m_optionValues;
    QList<ICmdOption*> m_options;
    QList<ICmdArgx*> m_argxes;
};

$PackageWebCoreEnd
