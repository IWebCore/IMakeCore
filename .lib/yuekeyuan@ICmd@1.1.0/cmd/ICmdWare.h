#pragma once

#include "core/util/IHeaderUtil.h"
#include "core/unit/IGadgetUnit.h"

$PackageWebCoreBegin

class ICmdAction;
class ICmdArgs;
class ICmdArgx;
class ICmdOptionValue;
class ICmdOption;
class ICmdWare : public IGadgetUnit
{
public:
    ICmdWare() = default;

protected:
    void parseAction(void* ptr, const QString& clsName, const QMap<QString, QString>& info, const QVector<QMetaMethod>& methods, const QVector<QMetaProperty>& props);

private:
    void findPrePath();
    void findOption();
    void findOptionValues();
    void findArgs();
    void findArgx();
    void createActions();
    void createAction(const QString& key);
    QStringList getActionPaths(const QString& funName);
    QMetaMethod getActionMethod(const QString& funName);
    QString getActionMemo(const QString& funName);

private:
    QMetaMethod findSetValueMethod(const QString& name, const QString& failReason);
    QMetaMethod findPreHandleMethod(const QString& name, const QString& failReason);
    QMetaMethod findPostHandleMethod(const QString& name, const QString& failReason);
    QMetaProperty findProperty(const QString& name);

private:
    void checkActionMethod(ICmdAction*);
    void checkOptionValueMethod(ICmdOptionValue*);
    void checkOptionMethod(ICmdOption*);
    void checkArgsMethod();
    void checkArgxMethod(ICmdArgx* argx);
    void checkOptionShortNameComflict();
    void checkHandleMethod(const QMetaMethod& method);

private:
    QStringList getMethodArguments(const QMetaMethod& method);

private:
    void *m_ptr;
    QMap<QString, QString> m_info;
    QVector<QMetaMethod> m_methods;
    QVector<QMetaProperty> m_props;

private:
    QString m_className;
    QStringList m_prePaths;
    ICmdArgs* m_args{};
    QList<ICmdOptionValue*> m_optionValues;
    QList<ICmdOption*> m_options;
    QList<ICmdArgx*> m_argxes;
    QList<ICmdAction*> m_actions;
};

$PackageWebCoreEnd
