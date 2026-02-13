loadToIncludes(${CMAKE_CURRENT_LIST_DIR})

loadToHeaders(
    ${CMAKE_CURRENT_LIST_DIR}/IHttpPythonTestAnnomacro.h
    ${CMAKE_CURRENT_LIST_DIR}/IHttpPythonTestTask.h
)
    
loadToSources(
    ${CMAKE_CURRENT_LIST_DIR}/IHttpPythonTestTask.cpp
)

loadToDefinitions(
    IWEBCORE_PROJECT_DIR="${CMAKE_SOURCE_DIR}"
)
