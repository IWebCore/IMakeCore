# IMakeCore2 完整流程

## 阶段一：安装（Installation）

执行 `windows_install.bat` 或 `linux_install.sh`，做两件事：

| 操作 | 细节 |
|------|------|
| **拷贝文件** | 把 `IMakeCore2/` 全部内容复制到系统固定位置。Windows: `%USERPROFILE%\IMakeCore`，Linux: `/opt/IMakeCore` |
| **注册环境变量** | 写入三个关键变量：`IMAKECORE_ROOT`、`IQMakeCore`、`ICMakeCore`，并把 `.programs/{platform}` 加到 `PATH` |

验证安装（`windows_install.bat` 第 54-56 行）：

```bat
setx IMAKECORE_ROOT "!target!" /m
setx IQMakeCore "%%IMAKECORE_ROOT%%/.system/.IMakeCore.prf" /m
setx ICMakeCore "%%IMAKECORE_ROOT%%/.system/.IMakeCore.cmake" /m
```

`.programs/windows/ipc.exe` 随 PATH 注册后可全局调用。

---

## 阶段二：接入项目（Package Resolution）

### 2.1 `ipc init` 做了什么

`ipc.exe` 是平台二进制工具。执行 `ipc init` 会在当前项目的 `.pro` 文件中插入三行：

```pro
include($$(IQMakeCore))        # ① 引入引擎
IQMakeCoreInit()               # ② 解析依赖
include($$PWD/.package.pri)    # ③ 导入结果
```

---

### 2.2 第①行：`include($$(IQMakeCore))`

`$$(IQMakeCore)` 展开为 `%IMAKECORE_ROOT%/.system/.IMakeCore.prf`。

这个文件定义了 **所有 qmake 侧的宏/函数**：`IQMakeCoreInit()`、`autoLoadPackage()`、`autoLoadHeaders/Sources/Includes/Definitions` 等，共 242 行。此时只是声明，尚未执行。

---

### 2.3 第②行：`IQMakeCoreInit()` —— 核心引擎

源码 `.IMakeCore.prf` 第 5-27 行：

```qmake
defineTest(IQMakeCoreInit){
    QMAKE_SOURCE_DIR = $$PWD
    findPythonInterpreter()                        # 找 python/python3
    script_path = $$getPythonFilePath("IMakeCore.py")
    cmd = $$python -B $$script_path $$PWD qmake    # 调用 Python
    res = $$system($$cmd, blob, result)            # 阻塞执行，捕获输出
    ! isEqual(result, 0) {
        error("packages configuration failed")
    }
}
```

本质是调用：`python -B .system/IMakeCore.py <项目目录> qmake`

### 2.4 Python 引擎执行链（`IMakeCore.py` 第 15-26 行）

```python
env = EnvConfig(appPath, packType)          # ① 构建环境
app = AppConfig(appPath)                    # ② 读取 packages.json
loadPackages(app, env)                      # ③ 解析每一个包
MakeUtils.updatePackageForceLocal(...)      # ④ 处理 forceLocal
MakeUtils.checkPackageDependencies(...)     # ⑤ 校验传递依赖
MakeUtils.createDumpJson(...)               # ⑥ 导出 dump.json
MakeUtils.createIncludeFile(packType, ...)  # ⑦ 生成 .package.pri
```

逐步拆解：

#### ① `EnvConfig` — 构建运行环境

`EnvConfig.__init__()`（`scripts/data/EnvConfig.py`）：

1. 从 `IMAKECORE_ROOT` 获取系统路径
2. 读取 `.data/config.json` → 获取 `servers[]`（下载源）、`globalLibStore`（全局包仓库）
3. **从 SQLite 数据库读取包索引**（`parseLibs()` — 查询 `package.db` 中的 `lib_package` 表），不再遍历文件系统
4. 创建必要的目录（缓存、数据、库存储）

> **包扫描已独立为 `updateDb.py`**。运行 `python scripts/updateDb.py` 会扫描所有系统包目录，将包元数据和文件列表写入 `package.db`。`IMakeCore.py` 仅从数据库读取。

#### ② `AppConfig` — 读取项目依赖声明

`AppConfig.__init__()`（`scripts/data/AppConfig.py`）：

1. 若项目目录下没有 `packages.json`，从模板 `IMAKECORE_ROOT/.data/packages.json` 复制一份
2. 解析 JSON 中的 `packages` 字段，每项生成 `AppPackage(name, version)`
3. `version == "x"` → 标记 `skip=True`，从依赖列表移除
4. `forceLocal` 继承自全局配置或包级覆盖

#### ③ `loadPackages()` — 逐个解析包

```python
def loadPackages(app, env):
    for package in app.packages:
        if not (LocatePackages(package, env).success
             or DownloadPackage(package, env).success):
            print(f"Failed...")
            exit(1)
```

对每个 `AppPackage`：
- **先本地找**：`LocatePackages` 在 `EnvConfig.libs`（已建好的索引）中匹配。匹配规则（`LibPackage.isMatch()`）：
  - 若包名含 `/`（如 `yuekeyuan/ICore`）→ 按 publisher + name + version 精确匹配
  - 若包名不含 `/` → 仅匹配 `isGlobal=true` 的同名包，version 走 SemVer 范围匹配
- **本地没有就下载**：`DownloadPackage` → 遍历 `servers[]`，请求 `GET /package/download?name=X&version=Y`，下载 zip → 解压 → `LibPackage` 加载验证

#### ④ `updatePackageForceLocal()`

`forceLocal: true` 的包会被 `shutil.copytree` 复制到项目自己的 `.lib/` 目录下（`MakeUtils.py` 第 53-68 行）。

#### ⑤ `checkPackageDependencies()`

遍历每个包的 `LibPackage.dependencies[]`（来自 `package.json` 的 `dependencies` 字段），确保所有传递依赖都在已解析的包列表中。不满足 → `exit(1)`。

#### ⑥ `createDumpJson()`

把解析结果写入 `项目/.data/dump.json`，方便调试查看。

#### ⑦ `createIncludeFile()` — 生成 .package.pri

`MakeUtils.qmakePostProcess()` 为每个包生成 per-library `.pri` 文件，放在项目的 `.lib/` 目录下。这些 per-library 文件从数据库（`lib_package_detail` 表）查询文件列表，直接写入 `SOURCES`、`HEADERS`、`INCLUDEPATH`、`DEFINES` 等 qmake 变量：

```pri
# SYSTEM AUTO GENERATED DO NOT EDIT!!!
# yuekeyuan@ICore@1.1.0
# core library for IWebCore

INCLUDEPATH += $$quote("C:/.../ICore/core/abort")
INCLUDEPATH += $$quote("C:/.../ICore/core/application")

HEADERS += $$quote("C:/.../ICore/core/abort/IAbortInterface.h")
HEADERS += $$quote("C:/.../ICore/core/application/IApplication.h")
...

SOURCES += $$quote("C:/.../ICore/core/abort/IGlobalAbort.cpp")
SOURCES += $$quote("C:/.../ICore/core/application/IApplication.cpp")
...
```

主 `.package.pri` 仅包含对各 per-library `.pri` 的 `include()` 语句：

```pri
include(C:/.../.lib/yuekeyuan@ICore@1.1.0.pri)
include(C:/.../.lib/yuekeyuan@nlohmann.json@3.12.0.pri)
```

**不再有 `autoLoadPackage()` 或 `autoScan` 机制** — 所有文件路径直接从数据库读取并在生成时写入。

---

### 2.5 第③行：`include($$PWD/.package.pri)` —— 导入所有包

这一行触发了对每个 per-library `.pri` 的 `include()`。每个 per-library `.pri` 文件已包含直接的 `SOURCES`、`HEADERS`、`INCLUDEPATH`、`DEFINES` 等声明，无需运行时扫描。

---

## 完整链路图

```
updateDb.py（手动执行，更新包数据库）
  │  └─ 扫描系统 libstores → 读 package.json + 扫描文件 → 写入 package.db
  │
用户执行 ipc init
  │
  ├─ 在 .pro 中插入 include($(IQMakeCore)) + IQMakeCoreInit() + include(.package.pri)
  │
  └─ qmake 执行时：
       │
       IQMakeCoreInit()
       │  └─ python IMakeCore.py <项目> qmake
       │       ├─ EnvConfig: 从 package.db 读取包索引（不再扫描文件系统）
       │       ├─ AppConfig: 读 packages.json 解析依赖
       │       ├─ LocatePackage: 本地匹配包（查询 env.libs，来自 DB）
       │       ├─ DownloadPackage: 未命中则从服务器下载
       │       ├─ checkDependencies: 验证传递依赖完整
       │       └─ createIncludeFile: 生成 .package.pri
       │              └─ 对每个包：查询 lib_package_detail 表 → 生成 per-library .pri
       │                   └─ 写入直接 SOURCES/HEADERS/INCLUDEPATH/DEFINES/FORMS/RESOURCES
       │
       include(.package.pri)
       │  └─ 对每个包 include(per-library .pri)
       │       └─ 直接引用文件路径（无运行时扫描）
       │
       └─ 最终：所有包的头文件/源文件/定义/资源已汇入 qmake 构建目标
```

### 新增：数据库维护

```bash
# 更新包数据库（安装/删除包后执行）
python -B .system/scripts/updateDb.py
```

数据库位置：`.system/db/package.db`

| 表 | 内容 |
|----|------|
| `lib_package` | 包元数据（名称、版本、发布者、依赖等） |
| `lib_package_detail` | 每个包的扫描文件列表（headers/sources/uis/resources/definitions/includes） |

---

## 关键环境变量

| 变量 | 值 | 用途 |
|------|-----|------|
| `IMAKECORE_ROOT` | 安装目录 | 所有路径解析的根 |
| `IQMakeCore` | `$ROOT/.system/.IMakeCore.prf` | qmake 项目的 include 入口 |
| `ICMakeCore` | `$ROOT/.system/.IMakeCore.cmake` | CMake 项目的 include 入口 |
| PATH 追加 | `$ROOT/.programs/{platform}` | 使 `ipc.exe` 全局可调用 |
