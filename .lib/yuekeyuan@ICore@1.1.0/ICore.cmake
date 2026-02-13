loadToIncludes(${CMAKE_CURRENT_LIST_DIR})

# QT += sql xml testlib
# CONFIG += c++17

# msvc {
#     debug {
#         QMAKE_CXXFLAGS += /bigobj
#     }
# }

# win32 {
#     LIBS += -lws2_32
#     LIBS += -lmswsock
# }

# PRECOMPILED_HEADER = ${CMAKE_CURRENT_LIST_DIR}/core/util/IHeaderUtil.h

find_package(Qt5 COMPONENTS Core Sql Test REQUIRED)

if(WIN32)
    loadToLibraries(
        ws2_32
        mswsock
    )

    loadToDefinitions(
        _WIN32_WINNT=0x0A00
    )

endif()


loadToSources(
    ${CMAKE_CURRENT_LIST_DIR}/core/abort/IGlobalAbort.cpp 
    ${CMAKE_CURRENT_LIST_DIR}/core/application/IAsioApplication.cpp 
    ${CMAKE_CURRENT_LIST_DIR}/core/application/IAsioContext.cpp 
    ${CMAKE_CURRENT_LIST_DIR}/core/application/default/IAsioTimer.cpp 
    ${CMAKE_CURRENT_LIST_DIR}/core/base/IException.cpp 
    ${CMAKE_CURRENT_LIST_DIR}/core/base/IString.cpp 
    ${CMAKE_CURRENT_LIST_DIR}/core/base/IStringView.cpp 
    ${CMAKE_CURRENT_LIST_DIR}/core/base/IStringViewStash.cpp 
    ${CMAKE_CURRENT_LIST_DIR}/core/base/IStringView_value.cpp 
    ${CMAKE_CURRENT_LIST_DIR}/core/base/IString_value.cpp 
    ${CMAKE_CURRENT_LIST_DIR}/core/bean/IBeanTypeManage.cpp 
    ${CMAKE_CURRENT_LIST_DIR}/core/config/IConfigManageInterface.cpp 
    ${CMAKE_CURRENT_LIST_DIR}/core/config/IConfigTaskCatagory.cpp 
    ${CMAKE_CURRENT_LIST_DIR}/core/config/IProfileManage.cpp 
    ${CMAKE_CURRENT_LIST_DIR}/core/config/default/IContextLoadSystemVariableTask.cpp 
    ${CMAKE_CURRENT_LIST_DIR}/core/config/default/ILoadProfileFileUnit.cpp 
    ${CMAKE_CURRENT_LIST_DIR}/core/config/default/IProfileLoadJsonTask.cpp 
    ${CMAKE_CURRENT_LIST_DIR}/core/task/ITaskCatagory.cpp 
    ${CMAKE_CURRENT_LIST_DIR}/core/task/ITaskManage.cpp 
    ${CMAKE_CURRENT_LIST_DIR}/core/task/ITaskWare.cpp 
    ${CMAKE_CURRENT_LIST_DIR}/core/task/default/IBannerTask.cpp 
    ${CMAKE_CURRENT_LIST_DIR}/core/task/default/IEndupTaskCatagory.cpp 
    ${CMAKE_CURRENT_LIST_DIR}/core/task/default/IInitializationTaskCatagory.cpp 
    ${CMAKE_CURRENT_LIST_DIR}/core/task/default/IRegistBaseTypeTask.cpp 
    ${CMAKE_CURRENT_LIST_DIR}/core/task/default/IRegistBaseTypeTask16bit.cpp 
    ${CMAKE_CURRENT_LIST_DIR}/core/task/default/IRegistBaseTypeTask32bit.cpp 
    ${CMAKE_CURRENT_LIST_DIR}/core/task/default/IRegistBaseTypeTask64bit.cpp 
    ${CMAKE_CURRENT_LIST_DIR}/core/task/default/IRegistBaseTypeTask8bit.cpp 
    ${CMAKE_CURRENT_LIST_DIR}/core/task/default/IRegistBaseTypeTaskBool.cpp 
    ${CMAKE_CURRENT_LIST_DIR}/core/task/default/IRegistBaseTypeTaskFloatingPoint.cpp 
    ${CMAKE_CURRENT_LIST_DIR}/core/task/default/IRegistBaseTypeTaskString.cpp 
    ${CMAKE_CURRENT_LIST_DIR}/core/task/default/IStartupTaskCatagory.cpp 
    ${CMAKE_CURRENT_LIST_DIR}/core/test/ITestCatagory.cpp 
    ${CMAKE_CURRENT_LIST_DIR}/core/test/ITestManage.cpp 
    ${CMAKE_CURRENT_LIST_DIR}/core/test/IUnitTestManage.cpp 
    ${CMAKE_CURRENT_LIST_DIR}/core/test/default/IFunctionTestTask.cpp 
    ${CMAKE_CURRENT_LIST_DIR}/core/test/default/IIntegrationTestTask.cpp 
    ${CMAKE_CURRENT_LIST_DIR}/core/test/default/IUnitTestTask.cpp 
    ${CMAKE_CURRENT_LIST_DIR}/core/unit/ISoloUnit.cpp 
    ${CMAKE_CURRENT_LIST_DIR}/core/util/ICodecUtil.cpp 
    ${CMAKE_CURRENT_LIST_DIR}/core/util/IConvertUtil.cpp 
    ${CMAKE_CURRENT_LIST_DIR}/core/util/IFileUtil.cpp 
    ${CMAKE_CURRENT_LIST_DIR}/core/util/IMetaUtil.cpp 
    ${CMAKE_CURRENT_LIST_DIR}/core/util/IPreProcessorUtil.cpp 
    ${CMAKE_CURRENT_LIST_DIR}/core/util/IStringUtil.cpp 
    ${CMAKE_CURRENT_LIST_DIR}/core/util/ITicTacUtil.cpp
)
