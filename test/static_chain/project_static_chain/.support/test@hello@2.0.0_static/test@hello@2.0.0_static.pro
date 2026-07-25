# test@hello@2.0.0 — DO NOT EDIT
TEMPLATE = lib
CONFIG += staticlib
TARGET = test@hello@2.0.0

include($$(IQMakeCore))
IQMakeCoreInit()
include($$PWD/.package.pri)

DESTDIR = $$PWD/$${QMAKE_HOST.arch}-pc-$${QMAKE_HOST.os}-$${QMAKE_SPEC}-static
