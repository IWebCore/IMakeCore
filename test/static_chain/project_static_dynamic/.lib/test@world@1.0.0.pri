# SYSTEM AUTO GENERATED DO NOT EDIT!!!
# test@world@1.0.0
# Test library that depends on hello

current_lib_path = "C:/Users/Yue/IMakeCore/test/static_chain/.lib/test@world@1.0.0"

INCLUDEPATH += \
    $$current_lib_path

win32-msvc*: LIBS += $$PWD/../.support/test@world@1.0.0_static/$${QMAKE_HOST.arch}-pc-$${QMAKE_HOST.os}-$${QMAKE_SPEC}-static/test@world@1.0.0.lib
else:        LIBS += $$PWD/../.support/test@world@1.0.0_static/$${QMAKE_HOST.arch}-pc-$${QMAKE_HOST.os}-$${QMAKE_SPEC}-static/libtest@world@1.0.0.a

