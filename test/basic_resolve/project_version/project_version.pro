include($$(IQMakeCore))
IQMakeCoreInit()
include($$PWD/.package.pri)

QT -= gui widgets
CONFIG += c++17 console
CONFIG -= app_bundle

SOURCES += main.cpp
