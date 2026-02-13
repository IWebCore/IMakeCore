#pragma once

#include <QtCore>
#include "core/util/IPackageUtil.h"
#include "core/base/IStringView.h"
#include "core/base/IString.h"

#ifndef __I_STRING_VIEW_STASH_GUARD__
#define __I_STRING_VIEW_STASH_GUARD__

$PackageWebCoreBegin

class IStringViewStash
{
public:
    IStringViewStash() = default;
    virtual ~IStringViewStash() = default;

public:
    IStringView stash(const char* data) const;
    IStringView stash(QByteArray&& data) const;
    IStringView stash(const QByteArray& data) const;
    IStringView stash(const QString& data) const;
    IStringView stash(std::string&& data) const;
    IStringView stash(const std::string& data) const;
    IStringView stash(IString&& data) const;
    IStringView stash(const IString& data) const;
    IStringView stash(IStringView data) const;

private:
    mutable std::list<IString> m_stashed;
};

$PackageWebCoreEnd

#endif
