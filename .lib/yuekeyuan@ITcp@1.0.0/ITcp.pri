INCLUDEPATH += $$PWD

HEADERS += \
    $$PWD/tcp/ITcpAbort.h \
    $$PWD/tcp/ITcpAnnomarco.h \
    $$PWD/tcp/ITcpConnection.h \
    $$PWD/tcp/ITcpConnectionData.h \
    $$PWD/tcp/ITcpManage.h \
    $$PWD/tcp/ITcpResolver.h \
    $$PWD/tcp/ITcpResolverFactoryInterface.h \
    $$PWD/tcp/ITcpResolverFactoryWare.h \
    $$PWD/tcp/ITcpServer.h \
    $$PWD/tcp/ITcpSocket.h \
    $$PWD/tcp/ITcpSocketFilterInterface.h \
    $$PWD/tcp/ITcpTaskCatagory.h

SOURCES += \
    $$PWD/tcp/ITcpConnection.cpp \
    $$PWD/tcp/ITcpConnectionData.cpp \
    $$PWD/tcp/ITcpManage.cpp \
    $$PWD/tcp/ITcpServer.cpp \
    $$PWD/tcp/ITcpSocket.cpp
