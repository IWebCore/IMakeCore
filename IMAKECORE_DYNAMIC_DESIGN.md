# IMakeCore 动态库支持 — 查漏补缺设计文档

> 日期: 2026-07-05 | 状态: 计划阶段 | 原则: 先不在代码上执行，反复确认后生成计划

---

## 1. 当前状态 vs 目标

### 1.1 当前支持

| 特性 | static | dynamic | source |
|------|--------|---------|--------|
| RefPackage.mode 声明 | ✅ | ✅ (未完整) | ✅ |
| header-only 拒绝 | ✅ | ✅ | ✅ |
| Support 子项目生成 | ✅ (.pro + CMakeLists.txt) | ❌ 未区分 | — |
| dynamicDefinition 校验 | 无 | ❌ | — |
| 主项目 LIBS 引用 | ✅ .a / .lib | ❌ 与 static 完全相同 | — |
| .bin 收集 | 无 | ❌ | — |
| 平台差异 (.dll+.lib vs .so) | ✅ | ❌ | — |
| ARCHIVE_OUTPUT_DIRECTORY | ✅ | ❌ 应该用 LIBRARY/RUNTIME | — |

### 1.2 目标

| 特性 | static | dynamic | source |
|------|--------|---------|--------|
| CONFIG | `staticlib` | `dll` | — |
| cmake add_library | `STATIC` | `SHARED` | — |
| 输出目录 ARCHIVE | `{arch}-{os}-{spec}-static` | `{arch}-{os}-{spec}-dynamic` | — |
| 输出目录 LIBRARY | — | 同上 (Linux .so) | — |
| 输出目录 RUNTIME | — | 同上 (Windows .dll) | — |
| dynamicDefinition 宏 | 无 | ✅ 从 resolve.dynamicDefinition 获取 | — |
| .bin 收集 | 无 | ✅ Windows .dll + Linux .so → .bin/ | — |
| 主项目 LIBS | .a / .lib | .so (Linux) / .dll+.lib (Win) | — |

---

## 2. 异议和问题清单

### 2.1 ⚠️ dynamicDefinition 从哪里来？

**用户描述**: "扫描 .lib 文件夹，如果一个库可以变成动态库，修改 package.json"

**问题**: 手动扫描 20 个库不现实。dynamicDefinition 应该是库的**作者**在 package.json 中声明的，不是安装后扫描的。

**建议**: 
- 库作者在 `package.json` 中添加 `resolve.dynamicDefinition`
- `updateDb.py` 将 `dynamicDefinition` 写入 DB 的 `LibPackageDetailTable.dynamic_definition` 字段（已存在）
- 不在安装脚本中做自动检测

### 2.2 ⚠️ ARCHIVE_OUTPUT_DIRECTORY 对动态库无效

**当前**: 子项目 cmake 只设置 `ARCHIVE_OUTPUT_DIRECTORY`（静态库输出目录）

**问题**: 动态库在 cmake 中有三个输出属性:
| 属性 | 用途 | 平台 |
|------|------|------|
| `ARCHIVE_OUTPUT_DIRECTORY` | 静态库 `.a`/`.lib` | 所有 |
| `LIBRARY_OUTPUT_DIRECTORY` | 动态库 `.so`/`.dylib` | Linux/macOS |
| `RUNTIME_OUTPUT_DIRECTORY` | 可执行文件 `.dll` | Windows |

**修复**: 动态库需要设置全部三个（或至少 LIBRARY + RUNTIME）

### 2.3 ⚠️ Windows 动态库需要 .lib 导入库

**问题**: 在 Windows 上链接动态库时，链接器需要 `.lib` 导入库（不是静态库的 `.lib`，是导入库）。主项目的 LIBS 路径需要同时指向 `.dll` 和 `.lib`。

**当前**: LIBS 只输出一个文件路径。

**修复**: 主项目 .pri 对动态库需要:
```qmake
win32: LIBS += .../myLib.lib   # 导入库
```

Linux 不需要导入库，直接链接 `.so`:
```qmake
unix: LIBS += .../libmyLib.so
```

### 2.4 ⚠️ qmake 的 `CONFIG += dll` 在子目录下行为

**问题**: `TEMPLATE = lib` + `CONFIG += dll` 在 qmake subdirs 构建中，输出目录由 qmake 决定，`DESTDIR` 可能不生效。

**需要实际测试验证**。

### 2.5 ⚠️ .bin 目录的权限问题

**问题**: 将 .dll/.so 拷贝到 `.bin/` 后，主程序运行时需要能找到这些文件。不同平台的搜索路径:
- Windows: 与 .exe 同级目录 → `.bin/` 不在搜索路径中，需要系统 PATH 或拷贝到 .exe 同级
- Linux: `LD_LIBRARY_PATH` 或 `rpath`
- macOS: `DYLD_LIBRARY_PATH` 或 `@rpath`

**建议**: `.bin/` 仅作为收集目录。实际部署时需要额外步骤（拷贝到 .exe 同级或设置 rpath）。

---

## 3. 完整设计

### 3.1 dynamicDefinition 校验（IMakeCore.py）

在 `_is_header_only` 检查之后添加:

```python
for ref in all_pkgs:
    if getattr(ref, "mode", "default") == "dynamic":
        lp = getattr(ref, "real_package", None)
        if lp is None:
            continue
        detail = _get_detail(lp)
        if detail is None or not detail.get_dynamic_definition():
            print(f"ERROR: Package '{lp.name}' mode='dynamic' but no dynamicDefinition"
                  f" found in package.json resolve section.")
            exit(1)
```

### 3.2 主项目 per-library dynamicDefinition 宏（QmakePackageGenerator）

在 `generate()` 中添加: 当 mode=dynamic 时，额外输出 dynamicDefinition 宏:

```python
if mode == "dynamic":
    dd = detail.get_dynamic_definition()
    if dd:
        for d in dd:
            lines.append(f"DEFINES += {d}")
```

同样在 CmakePackageGenerator 中添加:
```python
if mode == "dynamic":
    dd = detail.get_dynamic_definition()
    if dd:
        for d in dd:
            lines.append(f"target_compile_definitions(${{IMAKECORE_TARGET}} PRIVATE {d})")
```

### 3.3 子项目支持 dynamic（SupportLibGenerator._qmake_pro）

```qmake
TEMPLATE = lib
CONFIG += {'staticlib' if mode == 'static' else 'dll'}
TARGET = {target}
# ... IQMakeCore, IQMakeCoreInit, include(.package.pri)
DESTDIR = .../{mode}
```

### 3.4 子项目支持 dynamic（SupportLibGenerator._cmake_cmakelists）

```cmake
add_library({safe_target} {lib_type})   # STATIC or SHARED
set_target_properties({safe_target} PROPERTIES
    ARCHIVE_OUTPUT_DIRECTORY "...-{mode}"
    LIBRARY_OUTPUT_DIRECTORY "...-{mode}"    # .so 输出 (Linux)
    RUNTIME_OUTPUT_DIRECTORY "...-{mode}"    # .dll 输出 (Windows)
)
```

### 3.5 主项目 LIBS — 区分 static/dynamic（QmakePackageGenerator）

```python
if mode == "static":
    # 当前逻辑不变
    lines.append(f'else: LIBS += .../lib{target}.a')
elif mode == "dynamic":
    lines.append(f'win32: LIBS += .../{target}.lib')        # Windows 导入库
    lines.append(f'unix:  LIBS += .../lib{target}.so')       # Linux .so
```

### 3.6 主项目 LIBS — 区分 static/dynamic（CmakePackageGenerator）

```python
if mode == "static":
    # .a / .lib
elif mode == "dynamic":
    # Linux: .so, Windows: .dll + .lib
```

### 3.7 .bin 目录生成（IMakeCore.py，在 SupportLibGenerator 之后）

```python
if lib_pkgs:
    SupportLibGenerator(...).generate_all()
    dynamic_pkgs = [r for r in lib_pkgs if r.mode == "dynamic"]
    if dynamic_pkgs:
        BinCollector(dynamic_pkgs, pack_type, env).generate()
```

`BinCollector` 在 support 子项目编译后，将 .dll/.so 拷贝到 `.bin/`。

实际上 bin 收集应该在编译时完成（cmake/qmake 的 post-build step），而不是在 Python 生成阶段。应该在子项目的 .pro/CMakeLists.txt 中添加拷贝命令。

### 3.8 qmake 子项目 post-build 拷贝

```qmake
# 动态库：编译后拷贝到主项目 .bin/
dynamic {
    win32: QMAKE_POST_LINK += $$escape_expand(\\n) copy /Y $$DESTDIR/$${TARGET}.dll $$PWD/../../.bin/
    unix:  QMAKE_POST_LINK += cp $$DESTDIR/lib$${TARGET}.so $$PWD/../../.bin/
}
```

### 3.9 cmake 子项目 post-build 拷贝

```cmake
if(WIN32)
    add_custom_command(TARGET {safe_target} POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy_if_different
            "$<TARGET_FILE:{safe_target}>"
            "${CMAKE_CURRENT_SOURCE_DIR}/../../.bin/"
    )
endif()
```

对于 Linux: 只有一个 .so 文件，TARGET_FILE 会指向它。
对于 Windows: TARGET_FILE 指向 .dll（RUNTIME），需要额外复制 .lib（ARCHIVE）。

---

## 4. 文件变更清单

| 文件 | 变更 |
|------|------|
| `IMakeCore.py` | 添加 dynamicDefinition 校验 |
| `QmakePackageGenerator.py` | dynamic 分支：dynamicDefinition 宏 + 区分 LIBS |
| `CmakePackageGenerator.py` | dynamic 分支：dynamicDefinition 宏 + 区分 LIBS + ARCHIVE/LIBRARY/RUNTIME |
| `SupportLibGenerator.py` | dynamic 子项目：CONFIG+=dll / SHARED + post-build copy |
| `EnvConfig.py` | checkDirectoryExists 添加 `.bin/` |

---

## 5. 平台差异总表

| 方面 | Windows (MSVC/MinGW) | Linux (GCC) | macOS (Clang) |
|------|---------------------|-------------|---------------|
| 静态库后缀 | `.lib` / `.a`(MinGW) | `.a` | `.a` |
| 动态库后缀 | `.dll` | `.so` | `.dylib` |
| 导入库 | `.lib` (MSVC) / `.dll.a`(MinGW) | 无（直接链接 .so） | 无 |
| LIBS 引用 | `.lib` (导入库) | `.so` | `.dylib` |
| 运行时搜索 | PATH / 与 .exe 同级 | LD_LIBRARY_PATH / rpath | DYLD_LIBRARY_PATH / @rpath |
| 编译宏 | `__declspec(dllexport/dllimport)` | `__attribute__((visibility))` | 同 Linux |
| cmake 输出属性 | RUNTIME(.dll) + ARCHIVE(.lib) | LIBRARY(.so) | LIBRARY(.dylib) |
| qmake DESTDIR | 对 dll 有效 | 对 .so 有效 | 对 .dylib 有效 |

---

## 6. 待用户确认

| # | 问题 | 建议 |
|---|------|------|
| 1 | dynamicDefinition 谁来声明？ | 库作者在 package.json 中声明，不自动扫描 |
| 2 | .bin/ 收集后如何让运行时找到？ | .bin/ 仅收集。需要 rpath 或部署步骤 |
| 3 | MinGW 动态库导入库是 `.dll.a`，如何处理？ | 与 `.a` 静态库冲突，需特殊命名 |
| 4 | 是否需要 `QUAZIP_STATIC=0` 样的"禁止静态"宏？ | 建议省略 — mode 已由用户控制 |
