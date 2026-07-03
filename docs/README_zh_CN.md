# IMakeCore 包管理系统文档

## 概述

IMakeCore 是一个专为 C++ 项目设计的包管理系统，支持 qmake 和 cmake 两种构建系统。它能够自动化管理 C++ 依赖包的下载、定位、版本匹配和构建集成。

## 系统架构

```
IMakeCore
├── .system/                    # 系统核心目录
│   ├── IMakeCore.py           # 主入口脚本
│   ├── scripts/               # 核心功能模块
│   │   ├── data/             # 数据模型
│   │   │   ├── AppConfig.py  # 应用配置
│   │   │   ├── AppPackage.py # 应用包需求
│   │   │   ├── EnvConfig.py  # 环境配置
│   │   │   ├── LibPackage.py # 库包元数据
│   │   │   └── Utils.py      # 工具函数
│   │   ├── LocatePackage.py  # 本地包定位
│   │   ├── DownloadPackage.py # 远程包下载
│   │   └── MakeUtils.py      # 构建工具
│   └── .data/                # 系统数据
│       └── config.json       # 系统配置文件
├── .lib/                      # 全局库存储目录
└── .data/                    # 应用数据目录
```

## 核心概念

### 包命名规范

IMakeCore 使用统一的包命名格式：

```
publisher@name@version
```

例如：`yuekeyuan@ICore@1.1.0`

- **publisher**：发布者名称
- **name**：包名称
- **version**：语义化版本号

### 包类型

1. **全局包 (isGlobal: true)**
   - 可以被任何应用引用
   - 名称唯一性仅在发布者范围内保证

2. **本地包 (isGlobal: false)**
   - 必须指定发布者
   - 名称格式：`publisher/name`

### 包元数据 (package.json)

```json
{
    "name": "ICore",
    "version": "1.1.0",
    "publisher": "yuekeyuan",
    "isGlobal": true,
    "autoScan": true,
    "summary": "core library for IWebCore",
    "dependencies": {
        "nlohmann.json": "*"
    }
}
```

**字段说明：**

| 字段 | 类型 | 描述 |
|------|------|------|
| name | string | 包名称 |
| version | string | 版本号 (语义化版本) |
| publisher | string | 发布者标识 |
| isGlobal | boolean | 是否为全局包 |
| autoScan | boolean | 是否自动扫描集成 |
| summary | string | 包描述 |
| dependencies | object | 依赖包列表 |

## 包管理流程

### 1. 初始化阶段

```
AppConfig 加载
    ↓
读取 packages.json (应用层)
    ↓
读取 config.json (系统和应用层)
    ↓
解析服务器地址和库路径
    ↓
扫描本地库目录
```

### 2. 包定位流程 (LocatePackage)

```
开始定位
    ↓
检查用户指定路径 → 存在且匹配? → 是 → 成功返回
    ↓ 否
检查已加载的库缓存 → 找到匹配? → 是 → 成功返回
    ↓ 否
按包名模糊匹配搜索 → 找到匹配? → 是 → 成功返回
    ↓ 否
定位失败，需要下载
```

### 3. 包下载流程 (DownloadPackage)

```
开始下载
    ↓
检查是否有指定URL → 有 → 从URL下载
    ↓ 无
从配置的服务器列表下载
    ↓
下载为 .zip 文件到缓存目录
    ↓
验证下载内容 (检查 package.json)
    ↓
解压到库存储目录
    ↓
验证包版本是否匹配需求
```

### 4. 版本匹配规则

IMakeCore 使用 Python `packaging` 库进行版本匹配：

| 版本格式 | 示例 | 匹配规则 |
|----------|------|----------|
| 精确版本 | `1.1.0` | 必须完全匹配 |
| 通配符 | `*` | 匹配任意版本 |
| 范围 | `>=1.0.0,<2.0.0` | 符合 PEP 440 规范 |
| 跳过 | `x` | 跳过此包 |

### 5. 构建文件生成

#### qmake (.pri 文件)

```qmake
# SYSTEM CONFIGURED, DO NOT EDIT!!!
OTHER_FILES += packages.json 

# yuekeyuan@ICore@1.1.0
# core library for IWebCore
include(/path/to/yuekeyuan@ICore@1.1.0/yuekeyuan@ICore@1.1.0.pri)
```

#### CMake (.cmake 文件)

```cmake
###################################
# SYSTEM CONFIGURED, DO NOT EDIT!!!
###################################

# ICore@1.1.0
# core library for IWebCore
include(/path/to/yuekeyuan@ICore@1.1.0/yuekeyuan@ICore@1.1.0.cmake)
```

## 目录结构

### 系统目录

| 目录 | 说明 |
|------|------|
| `$IMAKECORE_ROOT/.lib/` | 全局库存储目录 |
| `$IMAKECORE_ROOT/.data/` | 系统数据目录 |
| `$IMAKECORE_ROOT/.cache/` | 下载缓存目录 |
| `$IMAKECORE_ROOT/.system/` | 系统核心文件 |

### 应用目录

| 目录 | 说明 |
|------|------|
| `APP_PATH/.lib/` | 应用本地库目录 |
| `APP_PATH/.data/` | 应用数据目录 |

## 配置文件

### 系统配置 (config.json)

```json
{
    "globalLibStore": ".lib",
    "libstores": [],
    "servers": [
        "http://115.191.52.106",
        "https://pub.iwebcore.org"
    ],
    "user": "default"
}
```

**配置项说明：**

| 字段 | 说明 |
|------|------|
| globalLibStore | 全局库存储路径 |
| libstores | 额外库搜索路径列表 |
| servers | 包下载服务器地址列表 |
| user | 当前用户标识 |

### 应用配置 (packages.json)

```json
{
    "localLibStore": ".lib",
    "forceLocal": false,
    "packages": {
        "ICore": ">=1.0.0",
        "nlohmann/json": "*",
        "custom/package": {
            "version": "1.0.0",
            "url": "https://example.com/package.zip",
            "path": "/custom/path",
            "forceLocal": true
        }
    }
}
```

**包配置格式：**

1. 简单格式：`"包名": "版本"`
2. 详细格式：
   ```json
   "包名": {
       "version": "版本要求",
       "url": ["下载地址"],
       "path": "本地路径",
       "forceLocal": false
   }
   ```

## 环境变量

| 变量名 | 说明 |
|--------|------|
| `IMAKECORE_ROOT` | IMakeCore 系统根目录 |
| `ICMakeCore` | CMake 配置文件路径 |
| `IQMakeCore` | qmake 配置文件路径 |

## 使用流程

### 1. 安装 IMakeCore

**Linux:**
```bash
sudo ./linux_install.sh
```

**Windows:**
```batch
.\windows_install.bat
```

### 2. 创建项目配置

在项目根目录创建 `packages.json`：

```json
{
    "packages": {
        "ICore": ">=1.1.0",
        "nlohmann/json": "*"
    }
}
```

### 3. 集成到构建系统

#### qmake (test.pro)

```qmake
QT += core
CONFIG += console
CONFIG -= app_bundle

include(IMakeCore/.system/IMakeCore.pri)
include(.package.pri)

SOURCES += main.cpp
```

#### CMake (CMakeLists.txt)

```cmake
cmake_minimum_required(VERSION 3.16)
project(test)

include(${ICMakeCore})
include(.package.cmake)

add_executable(test main.cpp)
```

### 4. 运行构建

IMakeCore 会在构建时自动：
1. 定位或下载所有依赖包
2. 验证依赖兼容性
3. 生成包配置文件
4. 集成到项目中

## 高级功能

### forceLocal 强制本地存储

设置 `forceLocal: true` 可以强制将包复制到应用的本地库目录：

```json
{
    "packages": {
        "myLib": {
            "version": "1.0.0",
            "forceLocal": true
        }
    }
}
```

### 自定义 URL 下载

可以指定包的下载地址：

```json
{
    "packages": {
        "customLib": {
            "version": "1.0.0",
            "url": "https://example.com/customLib.zip"
        }
    }
}
```

### 本地路径指定

可以直接指定本地包路径：

```json
{
    "packages": {
        "localLib": {
            "version": "1.0.0",
            "path": "/path/to/local/lib"
        }
    }
}
```

## 依赖检查

IMakeCore 在构建前会检查所有依赖：

1. **直接依赖**：在 `packages.json` 中声明的包
2. **传递依赖**：依赖包的 `dependencies` 中声明的包
3. **版本兼容性**：确保所有依赖版本满足要求

如果检测到缺失的依赖或版本不匹配，编译会失败并显示错误信息。

## 错误处理

| 错误类型 | 原因 | 解决方案 |
|----------|------|----------|
| 包未找到 | 包不存在或名称错误 | 检查包名拼写 |
| 版本不匹配 | 请求的版本不可用 | 调整版本要求 |
| 下载失败 | 网络问题或服务器不可用 | 检查网络连接 |
| 依赖缺失 | 传递依赖未声明 | 添加缺失依赖 |

## 技术实现

### 版本规范解析

使用 Python `packaging` 库实现：

```python
from packaging.version import Version
from packaging.specifiers import SpecifierSet

# 解析版本规范
spec = SpecifierSet(">=1.0.0,<2.0.0")
# 检查版本
if spec.contains(Version("1.5.0")):
    print("版本匹配")
```

### 包存储结构

```
.lib/
├── yuekeyuan@ICore@1.1.0/
│   ├── package.json
│   ├── core/
│   │   └── ...
│   └── yuekeyuan@ICore@1.1.0.pri
├── nlohmann@json@3.10.0/
│   ├── package.json
│   └── ...
```

## 总结

IMakeCore 提供了一个完整的 C++ 包管理解决方案：

- ✅ **自动化依赖管理**：无需手动下载和配置依赖
- ✅ **版本控制**：支持语义化版本和灵活的版本匹配
- ✅ **多构建系统支持**：同时支持 qmake 和 cmake
- ✅ **本地和全局库**：灵活的库存储策略
- ✅ **服务器支持**：可配置的远程包服务器
- ✅ **依赖传递**：自动处理传递依赖
