QT -= gui widgets
CONFIG += c++17 console
CONFIG -= app_bundle

SOURCES += main.cpp

# --- IMakeCore integration (env vars override, include at bottom) ---
IMAKECORE_ROOT = $$absolute_path($$PWD/../..)
IMAKECORE_SYSTEM = $$absolute_path($$PWD/../../../.system)
include($$(IQMakeCore))
IQMakeCoreInit()
include($$PWD/.package.pri)
