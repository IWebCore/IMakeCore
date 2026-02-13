# IHttpPythonTest
IWebCore extension used to test http request by python

## 配置测试路径说明
- 在`pro`文件中添加宏定义的方式,创建`QMAKE_PROJECT_DIR`变量,并赋值为测试目录

    ```pro
    DEFINES += QMAKE_PROJECT_DIR=\\\"$$PWD\\\"
    ```

- 在 `main.cpp` 文件中,使用宏定义的方式获取测试目录
    
    ```cpp
    #include <ICore/IApplication>
    #include <ICore/IContext>
    #include <IWeb/IHttpServer>
    #include "IHttpPythonTestAnnomacro.h"

    $EnableTaskOutput(true)
    $EnableHttpPythonTest(true)
    $SetHttpPythonScriptDir(D:/test)
    int main(int argc, char *argv[])
    {
        IApplication app(argc, argv);
        IHttpServer server;
        server.listen();
        return app.run();
    }
    ```

- 在配置文件中添加配置选项

    ```json
    {
        "test": {
            "pytest": {
                "enabled": true,
                "scriptDir": "D:/test"
            }
        }
    }
    ```

- 其他内容参考设计文档

