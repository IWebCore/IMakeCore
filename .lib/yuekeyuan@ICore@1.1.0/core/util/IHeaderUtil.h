#if !defined(__MINGW32__) && !defined(__MINGW64__)
    #pragma once
#endif

#ifndef  __IWEBCORE_IHEADERUTIL_GUARD__
#define  __IWEBCORE_IHEADERUTIL_GUARD__

#if __has_include(<asio.hpp>)
    #include <asio.hpp>
    #ifdef IWEBCORE_ENABLE_SSL
        #include <asio/ssl.hpp>
    #endif
#endif

#if __has_include(<json.hpp>)
    #include <json.hpp>
#endif

#if __has_include(<QtCore>)
    #include <QtCore>
#endif

#if __has_include(<QtSql>)
    #include <QtSql>
#endif

#if __has_include(<QtGui>)
    #include <QtGui>
#endif

#if __has_include(<QtWidgets>)
    #include <QtWidgets>
#endif

#include <type_traits>
#include "core/util/IPackageUtil.h"
#include "core/base/IJson.h"
#include "core/base/IString.h"
#include "core/base/IStringViewStash.h"
#include "core/base/IStringView.h"

#endif
