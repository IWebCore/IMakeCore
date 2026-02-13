#pragma once

#include "core/util/IHeaderUtil.h"

$PackageWebCoreBegin

class INodyParser;
struct INody
{
public:
    INody() = default;
    virtual ~INody() = default;

public:
    virtual INody* clone();

    virtual std::string execute(const IJson&, const QList<const IJson*>&) = 0;
    virtual void computeNody(INodyParser*){}

protected:
    IJson getValue(IStringView path, const IJson& global, const QList<const IJson*>& local);
};

struct INodyWithChildren
{
public:
    virtual ~INodyWithChildren();
public:
    QList<INody*> m_children;
};

struct INodyWithChild
{
public:
    virtual ~INodyWithChild();
public:
    INody* m_child{};
};

struct INodyWithTwins
{
public:
    virtual ~INodyWithTwins();
public:
    INody* m_elder{};
    INody* m_younger{};
};

#define $AsNody( klassName )    \
    virtual klassName * clone() final  \
    {   \
        auto node = new klassName(*this);   \
        node->INody::clone();   \
        return node;    \
    }


struct IContentNody : public INody, INodyWithChild
{
    $AsNody(IContentNody)
public:
    virtual std::string execute(const IJson&, const QList<const IJson*>&) final;
public:
    IString m_content;
};

struct IUnionNody : public INody, public INodyWithChildren
{
    $AsNody(IUnionNody)
public:
    virtual std::string execute(const IJson&, const QList<const IJson*>&) final;
};

struct IHtmlNody : public INody
{
    $AsNody(IHtmlNody)
public:
    virtual std::string execute(const IJson&, const QList<const IJson*>&) final;
public:
   IString m_html;
};

struct IVariableNody : public INody
{
    $AsNody(IVariableNody)
public:
    virtual std::string execute(const IJson&, const QList<const IJson*>&) final;
public:
    IString m_path;
};

struct IfNody : public INody, INodyWithTwins
{
    $AsNody(IfNody)
public:
    virtual std::string execute(const IJson&, const QList<const IJson*>&) final;
public:
    IString m_path;
};

struct IForNody : public INody, public INodyWithChild
{
    $AsNody(IForNody)
public:
    virtual std::string execute(const IJson&, const QList<const IJson*>&) final;
public:
    IString m_var;
    IString m_path;
};

struct IWithNody : public INody, public INodyWithChild
{
    $AsNody(IWithNody)
public:
    virtual std::string execute(const IJson&, const QList<const IJson*>&) final;
public:
    IString m_var;
    IString m_path;
};

struct IIncludeNody : public INody, public INodyWithChild
{
    $AsNody(IIncludeNody)
public:
    virtual std::string execute(const IJson&, const QList<const IJson*>&) final;
public:
    virtual void computeNody(INodyParser*) final;

public:
    IString m_path;
};

struct IBlockNody : public INody, public INodyWithChild
{
    $AsNody(IBlockNody)
public:
    virtual std::string execute(const IJson&, const QList<const IJson*>&) final;
public:
    IString m_name;
};

struct ISlotNody : public INody, public INodyWithChild
{
    $AsNody(ISlotNody)
public:
    virtual std::string execute(const IJson&, const QList<const IJson*>&) final;
public:
    IString m_name;
};

struct IExtendNody : public INody, public INodyWithChild, public INodyWithChildren
{
    $AsNody(IExtendNody)
public:
    virtual std::string execute(const IJson&, const QList<const IJson*>&) final;
    virtual void computeNody(INodyParser*) final;

private:
    void replaceBlock(INody* node, const QMap<IString, IBlockNody*>& map);

public:
    IString m_path;
};

struct IFunNody : public INody, public INodyWithChild
{
    $AsNody(IFunNody)
public:
    virtual std::string execute(const IJson&, const QList<const IJson*>&) final;
public:
    IString m_funName;
};

#undef $AsNody

$PackageWebCoreEnd
