# SYSTEM AUTO GENERATED DO NOT EDIT!!!
# test@hello@2.0.0
# Test source library v2 (contains .cpp)

current_lib_path = "C:/Users/Yue/IMakeCore/test/static_chain/.lib/test@hello@2.0.0"

INCLUDEPATH += \
    $$current_lib_path

HEADERS += \
    $$current_lib_path/hello.h

win32-msvc*: LIBS += $$PWD/../.support/test@hello@2.0.0_static/$${QMAKE_HOST.arch}-pc-$${QMAKE_HOST.os}-$${QMAKE_SPEC}-static/test@hello@2.0.0.lib
else:        LIBS += $$PWD/../.support/test@hello@2.0.0_static/$${QMAKE_HOST.arch}-pc-$${QMAKE_HOST.os}-$${QMAKE_SPEC}-static/libtest@hello@2.0.0.a

