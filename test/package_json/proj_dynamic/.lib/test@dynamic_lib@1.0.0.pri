# SYSTEM AUTO GENERATED DO NOT EDIT!!!
# test@dynamic_lib@1.0.0
# Test dynamic library

current_lib_path = "C:/Users/Yue/IMakeCore/test/package_json/.lib/test@dynamic_lib@1.0.0"

INCLUDEPATH += \
    $$current_lib_path

HEADERS += \
    $$current_lib_path/lib.h

DEFINES += sources
DEFINES += headers
win32-msvc*: LIBS += $$PWD/../.support/test@dynamic_lib@1.0.0_dynamic/$${QMAKE_HOST.arch}-pc-$${QMAKE_HOST.os}-$${QMAKE_SPEC}-dynamic/test@dynamic_lib@1.0.0.lib
win32-g++:  LIBS += $$PWD/../.support/test@dynamic_lib@1.0.0_dynamic/$${QMAKE_HOST.arch}-pc-$${QMAKE_HOST.os}-$${QMAKE_SPEC}-dynamic/libtest@dynamic_lib@1.0.0.a
macx: LIBS += $$PWD/../.support/test@dynamic_lib@1.0.0_dynamic/$${QMAKE_HOST.arch}-pc-$${QMAKE_HOST.os}-$${QMAKE_SPEC}-dynamic/libtest@dynamic_lib@1.0.0.dylib
linux: LIBS += $$PWD/../.support/test@dynamic_lib@1.0.0_dynamic/$${QMAKE_HOST.arch}-pc-$${QMAKE_HOST.os}-$${QMAKE_SPEC}-dynamic/libtest@dynamic_lib@1.0.0.so

