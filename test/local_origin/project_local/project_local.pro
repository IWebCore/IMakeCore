QT -= gui widgets
CONFIG += c++17 console
CONFIG -= app_bundle

SOURCES += main.cpp


message(root $$(IMAKECORE_ROOT))

message(abc $$IMAKECORE_ROOT)

IMAKECORE_ROOT = $$absolute_path($$PWD/../)
IMAKECORE_SYSTEM = $$(IMAKECORE_ROOT)/.system

message(root1 $$(IMAKECORE_ROOT))
message(abc1 $$IMAKECORE_ROOT)


include($$(IQMakeCore))
IQMakeCoreInit()
include($$PWD/.package.pri)
