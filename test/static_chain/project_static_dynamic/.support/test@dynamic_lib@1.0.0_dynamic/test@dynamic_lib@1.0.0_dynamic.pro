# test@dynamic_lib@1.0.0 — DO NOT EDIT
TEMPLATE = lib
CONFIG += dll
TARGET = test@dynamic_lib@1.0.0
DEFINES += sources
DEFINES += headers

include($$(IQMakeCore))
IQMakeCoreInit()
include($$PWD/.package.pri)

DESTDIR = $$PWD/$${QMAKE_HOST.arch}-pc-$${QMAKE_HOST.os}-$${QMAKE_SPEC}-dynamic

CONFIG(dll) {
    win32:  QMAKE_POST_LINK += $$quote(cmd /c copy /y $$shell_path($$DESTDIR/$${TARGET}.dll) $$shell_path($$PWD/../../.bin/))
    linux:  QMAKE_POST_LINK += cp -f $$shell_path($$DESTDIR/lib$${TARGET}.so*) $$shell_path($$PWD/../../.bin/)
    macx:   QMAKE_POST_LINK += cp -f $$shell_path($$DESTDIR/lib$${TARGET}.dylib) $$shell_path($$PWD/../../.bin/)
}
