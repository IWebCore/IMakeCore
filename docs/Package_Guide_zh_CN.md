# IMakeCore 包制作指南

## 概述

本指南介绍如何将 C++ 库制作成 IMakeCore 包，使其可以被 IMakeCore 包管理系统使用和分发。

## 包结构

一个完整的 IMakeCore 包需要包含以下文件：

```
publisher@name@version/
├── package.json           # 必需：包元数据
├── publisher@name@version.pri    # qmake 配置文件
├── publisher@name@version.cmake  # CMake 配置文件（可选）
└── [源代码目录...]
```

**注意**：包名目录的命名格式为 `publisher@name@version`，例如 `yuekeyuan@ICore@1.1.0`。

## 必需文件

### 1. package.json

包元数据文件，定义了包的基本信息和依赖关系。

**示例：**

```json
{
    "name": "ICore",
    "version": "1.1.0",
    "author": "yuekeyuan",
    "summary": "core library for IWebCore",
    "license": "AGPL-3.0-only",
    "keywords": ["core", "IWebCore", "annotation", "bean", "config", "dependency injection"],
    "links": [
        "https://github.com/IWebCore/ICore"
    ],
    "changelog": [
        "make asio as unnecessary dependency"
    ],
    "dependencies": {
        "nlohmann.json": "*",
        "ICore": ">=1.0.0"
    },
    "autoScan": true,
    "isGlobal": true,
    "publisher": "yuekeyuan"
}
```

**字段说明：**

| 字段 | 类型 | 必需 | 描述 |
|------|------|------|------|
| name | string | ✅ | 包名称 |
| version | string | ✅ | 语义化版本号 (如 1.0.0) |
| publisher | string | ✅ | 发布者标识 |
| summary | string | ✅ | 包简短描述 |
| author | string | ❌ | 作者名称 |
| license | string | ❌ | 许可证类型 |
| keywords | array | ❌ | 关键词列表 |
| links | array | ❌ | 相关链接 |
| changelog | array | ❌ | 更新日志 |
| dependencies | object | ❌ | 依赖包列表 |
| autoScan | boolean | ❌ | 是否自动扫描（默认 false） |
| isGlobal | boolean | ✅ | 是否为全局包 |

**dependencies 格式：**

```json
"dependencies": {
    "包名": "版本要求"
}
```

版本要求支持以下格式：
- 精确版本：`"1.0.0"`
- 通配符：`"*"` 或 `"x"`
- 版本范围：`">=1.0.0,<2.0.0"`

### 2. .pri 文件（qmake）

qmake 项目包含文件，用于 qmake 构建系统。

**示例：**

```qmake
INCLUDEPATH += $$PWD

# 预编译头文件（可选）
CONFIG += precompile_header
PRECOMPILED_HEADER = $$PWD/core/util/IHeaderUtil.h

# 平台特定配置
win32 {
    LIBS += -lws2_32
    LIBS += -lmswsock
}

linux {
    LIBS += -lpthread
}

# 头文件列表
HEADERS += \
    $$PWD/core/base/IException.h \
    $$PWD/core/base/IHandle.h \
    $$PWD/core/base/IJson.h

# 源文件列表
SOURCES += \
    $$PWD/core/base/IException.cpp \
    $$PWD/core/base/IJson.cpp
```

**关键要素：**

1. **INCLUDEPATH**：必须包含 `$$PWD`，指向包根目录
2. **HEADERS**：所有需要编译的头文件
3. **SOURCES**：所有需要编译的源文件
4. **平台适配**：使用 `win32 {}`、`linux {}`、`macx {}` 等条件块

### 3. .cmake 文件（CMake）

CMake 配置文件，用于 CMake 构建系统。

**示例：**

```cmake
loadToIncludes(${CMAKE_CURRENT_LIST_DIR})

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
    ${CMAKE_CURRENT_LIST_DIR}/core/base/IException.cpp
    ${CMAKE_CURRENT_LIST_DIR}/core/base/IJson.cpp
)
```

**关键要素：**

1. **loadToIncludes**：将包路径添加到包含目录
2. **find_package**：声明外部依赖（如 Qt5）
3. **loadToLibraries**：链接系统库
4. **loadToDefinitions**：添加编译定义
5. **loadToSources**：添加源文件

## 包类型

### 全局包 (isGlobal: true)

可以被任何应用引用，适用于通用库。

```json
{
    "name": "json",
    "isGlobal": true,
    "publisher": "nlohmann"
}
```

### 本地包 (isGlobal: false)

必须指定发布者，适用于私有或组织内部的库。

```json
{
    "name": "myLib",
    "isGlobal": false,
    "publisher": "myorg"
}
```

使用时需要用 `publisher/name` 格式引用：
```json
{
    "packages": {
        "myorg/myLib": ">=1.0.0"
    }
}
```

## autoScan 机制

### autoScan: true

启用自动扫描模式时，IMakeCore 会自动生成构建文件。

**自动生成的 .pri 文件内容：**

```qmake
# SYSTEM AUTO GENERATED DO NOT EDIT!!!
imakecore_current_lib_dir = "/path/to/package"
autoLoadPackage()
```

**自动生成的 .cmake 文件内容：**

```cmake
# SYSTEM AUTO GENERATED DO NOT EDIT!!!
set(imakecore_current_lib_dir "/path/to/package")
autoLoadPackage()
```

此时只需提供源代码目录结构，不需要手动编写完整的构建文件。

### autoScan: false

禁用自动扫描时，需要手动提供完整的 `.pri` 或 `.cmake` 文件。

## 发布流程

### 1. 准备包文件

1. 创建包目录：`publisher@name@version/`
2. 添加源代码文件
3. 创建 `package.json`
4. 创建 `.pri` 和/或 `.cmake` 文件

### 2. 打包为 ZIP

将整个包目录打包为 ZIP 文件：

```
publisher@name@version.zip
```

### 3. 上传到服务器

将 ZIP 文件上传到 IMakeCore 服务器的 `package/download` 端点。

**请求格式：**
```
GET /package/download?name={包名}&version={版本}
```

### 4. 创建包索引（可选）

在服务器上创建包索引文件：

```
packages/
├── publisher@name1@1.0.0.zip
├── publisher@name2@2.0.0.zip
└── ...
```

## 示例包结构

### 示例 1：纯头文件库

```
yuekeyuan@HTTPRequest@0.2.0/
├── package.json
├── HTTPRequest.hpp
└── README.md
```

**package.json：**

```json
{
    "name": "HTTPRequest",
    "version": "0.2.0",
    "author": "elnormous",
    "summary": "HTTPRequest is a single-header C++ library",
    "autoScan": true,
    "isGlobal": true,
    "publisher": "yuekeyuan"
}
```

### 示例 2：完整库

```
yuekeyuan@ICore@1.1.0/
├── package.json
├── ICore.pri
├── ICore.cmake
├── core/
│   ├── base/
│   │   ├── IException.h
│   │   ├── IException.cpp
│   │   └── ...
│   └── ...
└── README.md
```

### 示例 3：带依赖的库

```
yuekeyuan@ICmd@1.1.0/
├── package.json
├── ICmd.pri
├── ICmd.cmake
├── cmd/
│   └── ...
└── README.md
```

**package.json：**

```json
{
    "name": "ICmd",
    "version": "1.1.0",
    "summary": "cmd library for IWebCore",
    "dependencies": {
        "ICore": "*"
    },
    "autoScan": true,
    "isGlobal": true,
    "publisher": "yuekeyuan"
}
```

## 最佳实践

### 1. 版本命名

使用语义化版本 (Semantic Versioning)：

```
主版本.次版本.修订号
1.2.3
```

- **主版本**：不兼容的 API 变更
- **次版本**：向后兼容的功能添加
- **修订号**：向后兼容的 bug 修复

### 2. 依赖管理

- 尽量减少依赖数量
- 使用宽松的版本约束（如 `>=1.0.0` 而非 `==1.0.0`）
- 避免循环依赖

### 3. 文件组织

```
包名@版本/
├── package.json          # 元数据
├── 包名.pri              # qmake 配置
├── 包名.cmake            # CMake 配置
├── include/              # 头文件
│   └── 包名/
│       └── ...
├── src/                  # 源代码
│   └── ...
└── README.md             # 文档
```

### 4. 许可证

始终在 `package.json` 中明确指定许可证类型。

### 5. autoScan 使用

- 简单的库使用 `autoScan: true`
- 需要精细控制的库（如条件编译）使用 `autoScan: false`

## 常见问题

### Q: 找不到 .pri 或 .cmake 文件？

IMakeCore 按以下顺序查找：

**qmake (.pri)：**
1. `publisher@name@version.pri`
2. `name@version.pri`
3. `name.pri`
4. `.package.pri`

**CMake (.cmake)：**
1. `publisher@name@version.cmake`
2. `name@version.cmake`
3. `name.cmake`
4. `.package.cmake`

### Q: 如何处理外部依赖？

使用构建系统的依赖查找功能：

**qmake：**
```qmake
QT += network
CONFIG += link_pkgconfig
PKGCONFIG += libcurl
```

**CMake：**
```cmake
find_package(CURL REQUIRED)
include_directories(${CURL_INCLUDE_DIRS})
target_link_libraries(target ${CURL_LIBRARIES})
```

### Q: 如何处理条件编译？

使用平台条件块：

```qmake
win32 {
    # Windows 特定配置
}

linux {
    # Linux 特定配置
}

macx {
    # macOS 特定配置
}
```

### Q: 如何发布包到服务器？

1. 打包：`zip -r publisher@name@version.zip publisher@name@version/`
2. 上传 ZIP 文件到服务器
3. 确保服务器 `package/download` 端点可访问

## 总结

制作 IMakeCore 包的核心要点：

1. ✅ 创建正确的目录结构：`publisher@name@version/`
2. ✅ 编写 `package.json` 元数据文件
3. ✅ 提供 `.pri` 或 `.cmake` 构建文件
4. ✅ 设置 `autoScan: true` 简化配置
5. ✅ 声明所有依赖项
6. ✅ 打包为 ZIP 格式发布
