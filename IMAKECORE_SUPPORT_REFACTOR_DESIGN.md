# Support 代码库重构 + Deploy 目标设计

> 日期: 2026-07-05 | 状态: 设计阶段

---

## 1. 当前状态

### 1.1 现有文件

```
scripts/util/support/
├── __init__.py
├── SupportProjectFileGenerator.py   # 85行 - 生成 Support 总文件 (SUBDIRS/add_subdirectory)
└── SupportLibGenerator.py           # 113行 - 生成单个库子项目 (.pro/CMakeLists.txt) + condition
```

### 1.2 当前职责问题

| 文件 | 当前职责 | 问题 |
|------|---------|------|
| SupportLibGenerator | 子项目生成 + packages.json + condition + DB查询 + DEFINES | 职责过多, 113行 |
| SupportProjectFileGenerator | 总文件生成 + condition | 名称不一致 (File vs 无后缀) |

---

## 2. 目标架构

```
scripts/util/support/
├── __init__.py
├── SupportGenerator.py              # 入口, 协调其他 3 个
├── SupportProjectGenerator.py       # Support 总文件 (SUBDIRS + deploy)
├── SupportLibGenerator.py           # 单个库子项目
└── SupportDeployGenerator.py        # deploy 目标 (.bin/ 拷贝)
```

### 2.1 类的职责

#### SupportGenerator (NEW — 入口)

```python
class SupportGenerator:
    """协调 support 目录的所有生成工作"""
    def __init__(self, lib_packages, project_name, pack_type, env): ...

    def generate(self):
        """顺序调用 Project → Lib → Deploy"""
        os.makedirs(self.support_dir, exist_ok=True)
        SupportProjectGenerator(self.project_name, self.lib_packages, self.pack_type, self.env).generate()
        SupportLibGenerator(self.lib_packages, self.pack_type, self.env).generate_all()
        SupportDeployGenerator(self.lib_packages, self.project_name, self.pack_type, self.env).generate()
```

#### SupportProjectGenerator (RENAME from SupportProjectFileGenerator)

**不变**: 生成 master 文件 (SUBDIRS/add_subdirectory), condition 管理  
**新增**: 添加 deploy 目标的 SUBDIRS/依赖声明

#### SupportLibGenerator (精简)

**移除**: condition 管理 (移到 SupportProjectGenerator)  
**保留**: 单个库子项目生成 (.pro/CMakeLists.txt + packages.json)

#### SupportDeployGenerator (NEW)

**职责**: 在 master 文件中添加 deploy 目标

---

## 3. Deploy 目标设计

### 3.1 核心思想

deploy 目标在子目录项**最后**处理，收集所有动态库并拷贝到 `.bin/`。

### 3.2 qmake 实现

在 SupportProjectGenerator 生成的 `_Support.pro` 中追加:

```qmake
# deploy: 拷贝动态库 → .bin/
QMAKE_EXTRA_TARGETS += deploy
deploy.target = deploy_all
deploy.commands = $$PWD/imakecore_deploy.bat   # Windows
# 或 deploy.sh (Linux)

deploy.depends = $$SUBDIRS   # 等所有子项目编译完成

# 替换: 直接内联命令
# deploy.target = deploy_dlls
# deploy.CONFIG = recursive
# deploy.recurse = zlib_static zlib_dynamic
```

**问题**: qmake 的 `QMAKE_EXTRA_TARGETS` 对 SUBDIRS 模板支持有限。`deploy.depends` 不保证子目录先编译。

**替代方案 (更可靠)**: 在 condition 文件或单独的 `.pri` 中使用:

```qmake
# 在所有子项目编译后, 执行 deploy 步骤
deploy_targets.target = deploy
deploy_targets.depends = $$SUBDIRS
deploy_targets.commands = $$shell_path($$PWD/deploy_script.bat)
QMAKE_EXTRA_TARGETS += deploy_targets
```

但 `$$SUBDIRS` 在 Makefile 中是目录列表，`depends` 期望的是 target 名称，两者语义不匹配。

**实际方案: deploy 作为"库"子项目**

deploy 封装为 `.support/deploy/` 子目录，有自己的 `.pro`/`CMakeLists.txt`。利用 SUBDIRS `ordered` 自动保证在所有库之后编译。

#### qmake — deploy 作为库子项目

在 SupportProjectGenerator 生成的 `_Support.pro` 中，deploy 排在 SUBDIRS 最后:

```qmake
TEMPLATE = subdirs
CONFIG += ordered

SUBDIRS += yuekeyuan@zlib@1.3.1_dynamic\yuekeyuan@zlib@1.3.1_dynamic.pro
SUBDIRS += deploy\deploy.pro    # ← 最后, ordered 保证最后执行
```

`.support/deploy/deploy.pro`:
```qmake
TEMPLATE = aux

# Windows: copy .dll + import lib
win32 {
    QMAKE_POST_LINK += $$quote(cmd /c copy /y $$shell_path($$PWD/../yuekeyuan@zlib@1.3.1_dynamic/$${QMAKE_HOST.arch}-pc-$${QMAKE_HOST.os}-$${QMAKE_SPEC}-dynamic/*.dll) $$shell_path($$PWD/../../.bin/))
}
# Linux: copy .so
linux {
    QMAKE_POST_LINK += cp -f $$shell_path($$PWD/../yuekeyuan@zlib@1.3.1_dynamic/$${QMAKE_HOST.arch}-pc-$${QMAKE_HOST.os}-$${QMAKE_SPEC}-dynamic/lib*.so*) $$shell_path($$PWD/../../.bin/)
}
# macOS: copy .dylib
macx {
    QMAKE_POST_LINK += cp -f $$shell_path($$PWD/../yuekeyuan@zlib@1.3.1_dynamic/$${QMAKE_HOST.arch}-pc-$${QMAKE_HOST.os}-$${QMAKE_SPEC}-dynamic/lib*.dylib) $$shell_path($$PWD/../../.bin/)
}
```

**为什么可靠**: `CONFIG += ordered` 在 mingw32-make 和 nmake 下都保证 SUBDIRS 按声明顺序编译。deploy 排在最后 → 所有动态库已编译完成。

#### cmake — deploy 作为库子项目

```cmake
add_subdirectory(yuekeyuan@zlib@1.3.1_dynamic zlib_dynamic_build)
add_subdirectory(deploy deploy_build)    # ← 最后
```

`.support/deploy/CMakeLists.txt`:
```cmake
add_custom_target(imakecore_deploy ALL
    COMMAND ${CMAKE_COMMAND} -E make_directory "${CMAKE_CURRENT_SOURCE_DIR}/../../.bin"
)

add_dependencies(imakecore_deploy
    yuekeyuan_zlib_1_3_1    # 依赖每个动态库 target
)

add_custom_command(TARGET imakecore_deploy POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy_if_different
        "$<TARGET_FILE:yuekeyuan_zlib_1_3_1>"
        "${CMAKE_CURRENT_SOURCE_DIR}/../../.bin/"
)
```

`add_dependencies` 保证 cmake 在所有动态库 target 之后才执行 deploy 的 POST_BUILD。

### 3.3 平台差异

| 平台 | 拷贝命令 | 文件 |
|------|---------|------|
| Windows MSVC | `copy /Y` | `.dll` + `.lib` |
| Windows MinGW | `copy /Y` | `.dll` + `.a` (import lib) |
| Linux | `cp -f` | `.so` + `.so.1` (symlink) |
| macOS | `cp -f` | `.dylib` |

---

## 4. 文件变更清单

| 操作 | 文件 | 说明 |
|------|------|------|
| NEW | `SupportGenerator.py` | 入口协调类 |
| RENAME | `SupportProjectFileGenerator.py` → `SupportProjectGenerator.py` | 统一命名 |
| MODIFY | `SupportProjectGenerator.py` | 添加 deploy 目标到 support 文件 |
| MODIFY | `SupportLibGenerator.py` | 精简, 移除 condition |
| NEW | `SupportDeployGenerator.py` | deploy 目标生成 |
| MODIFY | `IMakeCore.py` | 用 SupportGenerator 替代直接调用 |
| MODIFY | `__init__.py` | 更新导出 |

---

## 5. 问题清单

### 5.1 ✅ deploy 顺序 — 已解决

通过"deploy 作为库子项目 + SUBDIRS ordered"解决。`CONFIG += ordered` 在 mingw32-make/nmake 下保证顺序。cmake 通过 `add_dependencies` 保证。

### 5.2 ⚠️ 文件后缀平台差异

deploy 子项目的拷贝命令需要覆盖:
- Windows: `.dll` + `.lib`(MSVC) / `.a`(MinGW)
- Linux: `.so` + `.so.1` 等 symlink
- macOS: `.dylib`

### 5.3 ⚠️ TEMPLATE = aux 的兼容性

qmake 的 `TEMPLATE = aux` 在某些旧版本不可用。备选: `TEMPLATE = subdirs` + 空的 SUBDIRS。

### 5.4 ⚠️ 重构 Breaking Change

`SupportProjectFileGenerator` 重命名为 `SupportProjectGenerator` 影响 IMakeCore.py import。

---

## 6. Deploy 生成示例

### 6.1 qmake output (in _Support.pro)

```qmake
TEMPLATE = subdirs
CONFIG += ordered
SUBDIRS += yuekeyuan@zlib@1.3.1_dynamic\yuekeyuan@zlib@1.3.1_dynamic.pro

# ── deploy: collect shared libs → .bin/ ──
deploy.target = imakecore_deploy
deploy.commands = $$PWD/imakecore_deploy.bat
deploy.CONFIG += phony
QMAKE_EXTRA_TARGETS += deploy
```

### 6.2 cmake output (in CMakeLists.txt)

```cmake
add_subdirectory(yuekeyuan@zlib@1.3.1_dynamic zlib_dynamic_build)

# ── deploy ──
add_custom_target(imakecore_deploy ALL)
add_dependencies(imakecore_deploy yuekeyuan_zlib_1_3_1)
add_custom_command(TARGET imakecore_deploy POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E make_directory "${CMAKE_CURRENT_SOURCE_DIR}/../.bin"
    COMMAND ${CMAKE_COMMAND} -E copy_if_different
        "$<TARGET_FILE:yuekeyuan_zlib_1_3_1>"
        "${CMAKE_CURRENT_SOURCE_DIR}/../.bin/"
)
```

---

## 7. 总结

| 项目 | 状态 |
|------|------|
| 类拆分 (4 个) | 设计清晰, 可直接实施 |
| Deploy 目标 (qmake) | 独立 make target, 手动调用 |
| Deploy 目标 (cmake) | 自动执行, 通过 add_dependencies |
| 平台差异 | 需在 deploy 脚本中处理 |
| Breaking changes | IMakeCore.py import 需更新 |
