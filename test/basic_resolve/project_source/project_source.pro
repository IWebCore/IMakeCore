# Test environment
IMAKECORE_ROOT = C:\Users\Yue\IMakeCore\test\basic_resolve
IMAKECORE_SYSTEM = C:\Users\Yue\IMakeCore\.system

include($$(IQMakeCore))
IQMakeCoreInit()
include($$PWD/.package.pri)

QT -= gui widgets
CONFIG += c++17 console
CONFIG -= app_bundle

SOURCES += main.cpp
