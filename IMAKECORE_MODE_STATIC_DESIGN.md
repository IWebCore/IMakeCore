# IMakeCore mode=static/dynamic 支持 — 完整设计文档

> 日期: 2026-07-04 | 状态: 设计定稿 | 融合 14 个用户确认回答

---

## 1. 核心设计变更

### 1.1 LibPackage.mode: 字符串 → JSON 数组

**旧**: `LibPackageTable.mode = String(50)`, 默认 `"sources"`
**新**: `LibPackageTable.mode = JSON` (数组), 默认 `["source","static"]`

含义: 此包支持的导入方式列表。
- 如果 package.json 中 mode 未定义 → `["source", "static"]`
- 如果定义为 `"static"` → `["static"]`
- 如果定义为 `["source","dynamic"]` → 支持源码和动态两种方式

校验: 数组每个元素 ∈ {source, static, dynamic}

### 1.2 RefPackage.mode 保持单值字符串

用户声明想要的方式。默认 `"default"` 等效 `"source"`。
校验: ∈ {source, static, dynamic, default}

### 1.3 匹配规则

```
PackageResolver.isMatch(ref, lib):
    ... (现有 publisher/name/version 匹配) ...
    AND ref.mode ∈ lib._supported_modes  (用户要求的模式必须在包支持列表中)
```

例如: 包 A 的 package.json 中 mode=["source"] → 用户以 static 引用时匹配失败。

---

## 2. mode 完整语义

| 值 | 主项目 per-library 输出 | 不输出 | 编译方式 |
|----|-----------------------|--------|---------|
| source/default | HEADERS + SOURCES + INCLUDEPATH + FORMS + RESOURCES + DEFINES | — | 主项目直接编译源码 |
| static | HEADERS + INCLUDEPATH + DEFINES + LIBS | SOURCES, FORMS, RESOURCES | support 子项目编译为静态库(.a/.lib) |
| dynamic | 同 static + dynamicDefinition 宏 + Windows .lib | SOURCES, FORMS, RESOURCES | support 子项目编译为动态库(.so/.dll) |

### 2.1 static vs dynamic 唯一区别

| 方面 | static | dynamic |
|------|--------|---------|
| 编译器输出 | .a (Linux) / .lib (Windows) | .so (Linux) / .dll+.lib (Windows) |
| 主项目引用 | LIBS += lib.a | LIBS += lib.so (+ lib.lib on Win) |
| 宏定义 | 无 | dynamicDefinition 字段内容 |
| Windows 导入库 | 无 | .lib 文件 |
| qmake CONFIG | staticlib | dll |
| cmake add_library | STATIC | SHARED |

**其他方面完全一致** — 头文件引用、includePath、构建系统集成、依赖顺序。

---

## 3. .support 目录完整布局

```
{project}/
├── .support/
│   ├── ProjectName_Support.pro          (qmake: TEMPLATE=subdirs)
│   或 CMakeLists.txt                 (cmake: add_subdirectory)
│   │
│   ├── yuekeyuan@ICore@1.1.0_static/    (static/dynamic 子项目)
│   │   ├── packages.json                (source 模式, 引用该库自身)
│   │   ├── yuekeyuan@ICore@1.1.0_static.pro
│   │   或 CMakeLists.txt
│   │   └── x86_64-pc-win32-msvc-static/ (build 输出)
│   │       └── libICore.a
│   │
│   └── yuekeyuan@ICmd@1.1.0_static/
│       └── ...
│
├── .lib/  (per-library .pri/.cmake 文件)
├── .package.pri / .package.cmake
└── packages.json
```

### 3.1 Support 总文件

**qmake** — 声明依赖顺序:

```qmake
TEMPLATE = subdirs
CONFIG += ordered

SUBDIRS += yuekeyuan@ICore@1.1.0_static   # 先编译这个
SUBDIRS += yuekeyuan@ICmd@1.1.0_static
SUBDIRS += ..                               # 主项目最后
```

**cmake** — 声明依赖顺序:

```cmake
cmake_minimum_required(VERSION 3.16)
project(ProjectName_Support)

add_subdirectory(yuekeyuan@ICore@1.1.0_static ICore_build)
add_subdirectory(yuekeyuan@ICmd@1.1.0_static ICmd_build)
add_subdirectory(.. .main_build)

add_dependencies(main_EXECUTABLE ICore ICmd)
```

### 3.2 总是生成

无论有没有 static/dynamic 包，Support 文件总是生成。无 lib 包时只有主项目一个条目。

---

## 4. 子项目文件

### 4.1 qmake (.pro)

```qmake
# yuekeyuan@ICore@1.1.0 — DO NOT EDIT
TEMPLATE = lib
CONFIG += staticlib                    # static: staticlib | dynamic: dll
TARGET = yuekeyuan@ICore@1.1.0

include($$(IQMakeCore))
IQMakeCoreInit()

# 输出目录: {arch}-pc-{os}-{abi}-{mode}
DESTDIR = $$PWD/$${QMAKE_HOST.arch}-pc-$${QMAKE_HOST.os}-$${QMAKE_HOST.abi}-static
```

### 4.2 cmake (CMakeLists.txt)

```cmake
# yuekeyuan@ICore@1.1.0 — DO NOT EDIT
cmake_minimum_required(VERSION 3.16)
project(yuekeyuan@ICore@1.1.0_static)

add_library(yuekeyuan@ICore@1.1.0 STATIC)   # static: STATIC | dynamic: SHARED

set_target_properties(yuekeyuan@ICore@1.1.0 PROPERTIES
    ARCHIVE_OUTPUT_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}/${CMAKE_SYSTEM_PROCESSOR}-${CMAKE_SYSTEM_NAME}-static"
)

include($ENV{ICMakeCore})
ICmakeCoreInit(yuekeyuan@ICore@1.1.0)
```

### 4.3 架构命名 (使用 qmake/cmake 内置变量)

| 组件 | qmake | cmake | 示例 |
|------|-------|-------|------|
| arch | `QMAKE_HOST.arch` | `CMAKE_SYSTEM_PROCESSOR` | x86_64, arm64 |
| vendor | 固定 `pc` | 固定 `unknown` | pc |
| os | `QMAKE_HOST.os` | `CMAKE_SYSTEM_NAME` | win32, linux, darwin |
| abi | `QMAKE_HOST.abi` | `CMAKE_CXX_COMPILER_ID` | msvc, gnu |
| mode | 固定 `static`/`dynamic` | 固定 `static`/`dynamic` | static |

**目录格式**：`{arch}-{vendor}-{os}-{abi}-{mode}`

示例输出:
- Windows MSVC: `x86_64-pc-win32-msvc-static`
- Linux GCC: `x86_64-pc-linux-gnu-static`
- macOS: `arm64-apple-darwin-static`

### 4.4 子项目 packages.json (source 模式引用自身)

```json
{
    "packages": {
        "yuekeyuan/ICore": "*"
    }
}
```

这样子项目的 `IQMakeCoreInit()` 会生成 `.package.pri`，让编译器获得该库的所有源文件。

---

## 5. 主项目 per-library 按 mode 区分

### 5.1 mode=source/default — 当前行为不变

```pri
current_lib_path = "C:/IMakeCore/.lib/yuekeyuan@ICore@1.1.0"
INCLUDEPATH += $$current_lib_path
HEADERS += $$current_lib_path/core/IAbortInterface.h ...
SOURCES += $$current_lib_path/core/IGlobalAbort.cpp ...
```

### 5.2 mode=static

```pri
current_lib_path = "C:/IMakeCore/.lib/yuekeyuan@ICore@1.1.0"
INCLUDEPATH += $$current_lib_path
HEADERS += $$current_lib_path/core/IAbortInterface.h ...
DEFINES += USE_ICORE
LIBS += $$PWD/../.support/yuekeyuan@ICore@1.1.0_static/x86_64-pc-win32-msvc-static/libICore.a
```

**不输出**: SOURCES, FORMS, RESOURCES

### 5.3 mode=dynamic

```pri
current_lib_path = "C:/IMakeCore/.lib/yuekeyuan@ICore@1.1.0"
INCLUDEPATH += $$current_lib_path
HEADERS += $$current_lib_path/core/IAbortInterface.h ...
DEFINES += ICORE_DYNAMIC_EXPORT          # dynamicDefinition 宏
DEFINES += USE_ICORE

# Linux
LIBS += $$PWD/../.support/yuekeyuan@ICore@1.1.0_dynamic/x86_64-pc-linux-gnu-dynamic/libICore.so

# Windows (额外 .lib 导入库)
LIBS += $$PWD/../.support/yuekeyuan@ICore@1.1.0_dynamic/x86_64-pc-win32-msvc-dynamic/ICore.lib
```

### 5.4 路径计算

生成器在生成 per-library 文件时，计算从 `.lib/` 到 `.support/` 的相对路径:

```python
support_dir = os.path.join(env.appPath, ".support")
per_lib_dir = env.appLibStore
rel = os.path.relpath(support_dir, per_lib_dir)   # 示例: ../../../../.support
```

在 .pri 中写入: `LIBS += $$PWD/{rel}/{pkg}_static/{arch_dir}/lib{name}.{ext}`

### 5.5 平台差异

| 平台 | static 后缀 | dynamic 后缀 | 导入库 |
|------|-----------|-------------|--------|
| Windows | .lib | .dll | .lib (同名) |
| Linux | .a | .so | — |
| macOS | .a | .dylib | — |

生成器根据 `sys.platform` 或 `platform.system()` 选择正确后缀。

---

## 6. 类结构

### 6.1 SupportProjectFileGenerator

`scripts/util/support/SupportProjectFileGenerator.py`

```python
class SupportProjectFileGenerator:
    def __init__(self, project_name, lib_packages, pack_type, env):
        # lib_packages: static + dynamic 包的 RefPackage 列表
        ...

    def generate(self):
        """生成 .support/{ProjectName}_Support.pro 或 CMakeLists.txt
        - 创建 .support/ 目录
        - 按 mode 分组生成 SUBDIRS / add_subdirectory
        - 主项目排在最后
        - 总是生成 (无 lib 包时只有主项目)
        """
```

### 6.2 SupportLibGenerator

`scripts/util/support/SupportLibGenerator.py`

```python
class SupportLibGenerator:
    def __init__(self, lib_packages, pack_type, env): ...

    def generate_all(self):
        """为每个 static/dynamic 包:
        1. 创建 .support/{pkg}_static/ 目录
        2. 写入 packages.json (source 模式)
        3. 写入 .pro 或 CMakeLists.txt
        """

    def generate_one(self, ref: RefPackage):
        """单个子项目生成"""
```

### 6.3 QmakePackageGenerator / CmakePackageGenerator

在 `generate()` 开头获取 mode，按 mode 分支:

```python
def generate(self, pkg, env):
    ...
    mode = getattr(pkg, "mode", "default")

    if mode in ("static", "dynamic"):
        self._emit_includes(lines, includes)
        self._emit_definitions(lines, definitions)
        self._emit_continuation(lines, "HEADERS", headers, ...)
        self._emit_lib_link(lines, pkg, mode, env)
        if mode == "dynamic":
            self._emit_dynamic_def(lines, dynamic_definitions)
    else:
        # 全额输出（现有行为）
        ...
```

---

## 7. RefPackage 工厂重构 (用户确认 9.6)

将 `from_string` 和 `from_config` 合并为一个入口:

```python
class RefPackage:
    @classmethod
    def from_package_json(cls, name, value, app_data):
        """
        name: "ICore" 或 "yuekeyuan/ICore"
        value: "*" 或 {"version": ">=1.0", "mode": "static", ...}
        app_data: AppData 实例
        """
        publisher, pkg_name, is_global = LibPackage.split_name(name)

        if isinstance(value, str):
            return cls._from_string_impl(pkg_name, value, app_data.global_origin,
                                         publisher, is_global)
        if isinstance(value, dict):
            return cls._from_config_impl(pkg_name, value, app_data.global_origin,
                                         publisher, is_global)
        print(f"ERROR: Invalid package value for '{name}'.")
        exit(1)
```

AppData 简化为:

```python
def _parse_one(self, name, value):
    ref = RefPackage.from_package_json(name, value, self)
    return ref if not ref.skip else None
```

移除 AppData 中的 `_parse_git`（已在 RefPackage 中）。

---

## 8. 集成流程

```
IMakeCore.py

env = EnvConfig(appPath, packType)
app_data = AppData(appPath)

resolver = PackageResolver(app_data, env)
resolver.resolve_all()                         # 含 mode 匹配

all_pkgs = app_data.all_packages()

# 按 mode 分离
source_pkgs = [r for r in all_pkgs if getattr(r,'mode','default') in ('source','default')]
lib_pkgs    = [r for r in all_pkgs if getattr(r,'mode','default') in ('static','dynamic')]

# 主项目生成 (generator 内部判断 mode)
MakeUtils.checkPackageDependencies(all_pkgs)
MakeUtils.createDumpJson(all_pkgs, env)
MakeUtils.createIncludeFile(packType, all_pkgs, env)

# Support 项目 (only if lib_pkgs non-empty)
project_name = os.path.basename(appPath)
MakeUtils.createSupportProject(project_name, lib_pkgs, packType, env)

app_data.save_cache()
```

---

## 9. 文件变更清单

| # | 文件 | 变更 | 说明 |
|---|------|------|------|
| 1 | `scripts/data/RefPackage.py` | REWRITE | factory 合并为 `from_package_json()` |
| 2 | `scripts/data/AppData.py` | SIMPLIFY | `_parse_one` 一行委托 |
| 3 | `scripts/data/LibPackage.py` | MODIFY | mode 改数组, isMatch 加 mode 校验 |
| 4 | `scripts/data/models.py` | MODIFY | LibPackageTable.mode String→JSON |
| 5 | `scripts/util/PackageResolver.py` | MODIFY | resolve_one 加 mode 匹配 |
| 6 | `scripts/util/make/QmakePackageGenerator.py` | MODIFY | generate() mode 分支 |
| 7 | `scripts/util/make/CmakePackageGenerator.py` | MODIFY | generate() mode 分支 |
| 8 | `scripts/IMakeCore.py` | MODIFY | 加 support 生成 |
| 9 | `scripts/MakeUtils.py` | MODIFY | createSupportProject() |
| 10 | `scripts/updateDb.py` | MODIFY | mode 存为 JSON 数组 |
| 11 | `scripts/data/EnvConfig.py` | MODIFY | checkDirectoryExists 加 .support/ |
| 12 | **NEW** `scripts/util/support/__init__.py` | NEW | |
| 13 | **NEW** `scripts/util/support/SupportProjectFileGenerator.py` | NEW | |
| 14 | **NEW** `scripts/util/support/SupportLibGenerator.py` | NEW | |

---

## 10. 待定项 — 全部已确认 ✅

| # | 问题 | 回答 |
|---|------|------|
| 1 | mode 是数组还是单值 | **LibPackage.mode = JSON数组** (支持列表), RefPackage.mode = 单值(用户选择) |
| 2 | 匹配时 mode 不匹配 | 库不匹配, resolve 失败 |
| 3 | dynamic vs static 区别 | dynamic 多 dynamicDefinition 宏 + Windows .lib |
| 4 | Support 总是生成 | 是, 无 lib 包时只有主项目 |
| 5 | 子项目需要 packages.json | 是, source 模式引用自身 |
| 6 | 库路径用相对 | 是, 生成时计算 |
| 7 | factory 重构 | from_package_json(name, value, app_data) |
| 8 | 架构命名 | qmake/cmake 内置变量 |
| 9 | qmake/cmake 隔离 | 各自独立, 不互处理 |
