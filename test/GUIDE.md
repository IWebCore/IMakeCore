# IMakeCore 功能测试 — 完整指南

> 本文档描述如何为 IMakeCore 创建功能测试。每一个测试都是一个**自包含的独立环境**，
> 拥有自己的 `.system/`（代码）、`.lib/`（虚拟包）、`.data/`（配置）、`.db/`（数据库）。
> 读完本文档后，你可以从零开始创建一个新的测试，无需任何额外上下文。

---

## 目录

1. [概念：什么是 IMAKECORE_ROOT](#1-概念什么是-imakecore_root)
2. [测试目录结构](#2-测试目录结构)
3. [从零创建子测试（Step-by-Step）](#3-从零创建子测试step-by-step)
4. [创建虚拟包（Fixture）](#4-创建虚拟包fixture)
5. [编写 test.py](#5-编写-testpy)
6. [验证模式参考](#6-验证模式参考)
7. [运行测试](#7-运行测试)
8. [添加 HTTP 下载测试](#8-添加-http-下载测试)
9. [故障排查](#9-故障排查)
10. [测试文档同步规则](#10-测试文档同步规则)
11. [项目文件模板 (.pro / CMakeLists.txt)](#11-项目文件模板-pro--cmakeliststxt)
12. [package.json 字段参考](#12-packagejson-字段参考)

---

## 1. 概念：什么是 IMAKECORE_ROOT

IMakeCore 运行时依赖一个名为 `IMAKECORE_ROOT` 的环境变量，它指向以下结构的目录：

```
$IMAKECORE_ROOT/
├── .system/           ← Python 代码本体（IMakeCore.py, scripts/, resolvelib/ 等）
│   ├── IMakeCore.py           ← 入口
│   ├── scripts/
│   │   ├── updateDb.py        ← 扫描 .lib/ 中的包，写入 SQLite 数据库
│   │   └── data/
│   │       └── models.py      ← SQLAlchemy 模型和数据库引擎
│   └── db/                    ← 【旧】数据库路径（已被 .db/ 替代）
├── .lib/              ← 系统级包存储。每个子目录是一个包，格式为 {publisher}@{name}@{version}
├── .data/             ← 系统配置文件
│   ├── config.json            ← servers[], libstores[], globalLibStore, user
│   └── packages.json          ← 空模板（新项目会复制此文件）
└── .db/               ← SQLite 数据库
    └── package.db             ← update_db.py 扫描 .lib/ 后生成的包索引
```

**测试的核心思路**：为每个测试场景创建一个完整的、独立的 `IMAKECORE_ROOT`。

> **注意**：`IMAKECORE_ROOT` 只需包含 `.lib/`、`.data/`、`.db/`。`.system/` 代码目录通过独立的
> `IMAKECORE_SYSTEM` 环境变量指向项目根的真实 `.system/`，无需在每个测试目录中复制或 junction。
> `run_all.py` 启动时自动设置此变量。

---

## 2. 测试目录结构

```
test/
├── run_all.py                   ← 主运行器
├── tests.pro                    ← Qt Creator 入口：TEMPLATE=subdirs 包含所有 project_*
├── CMakeLists.txt               ← CMake 入口：add_subdirectory 包含所有 project_*
├── GUIDE.md                     ← 本文档
├── TEST_SPEC.md                 ← 所有测试用例的清单
├── fixtures/                    ← 【共享】虚拟包模板
│   ├── test@hello@1.0.0/        ← 目录名 = 包的唯一标识
│   │   ├── package.json
│   │   └── hello.h              ← （可选）决定 header-only vs source
│   └── ...
│
├── basic_resolve/               ← 子测试：基本包解析
│   ├── test.py                  ← 测试脚本
│   ├── project_single/          ← 测试项目（持久保留，可 IDE 打开）
│   │   ├── packages.json
│   │   ├── project_single.pro   ← Qt .pro 文件
│   │   ├── CMakeLists.txt       ← CMake 文件
│   │   ├── main.cpp             ← 入口（引用解析到的头文件）
│   │   ├── .package.pri         ← IMakeCore 生成
│   │   └── .lib/                ← 项目本地包
│   └── ...
│
└── static_chain/
    └── ...
```

**IDE 使用**：用 Qt Creator 打开 `test/tests.pro` 或 `test/CMakeLists.txt`，即可将所有 75 个测试项目导入 IDE。
    └── （结构同上）
```

**关键规则**：

- 每个子测试目录**本身就是** `IMAKECORE_ROOT`
- `.system/` 是到真实代码的 **junction**（Windows）/ **symlink**（Linux），不复制
- `.lib/`、`.data/`、`.db/` 是真实目录，完全独立
- 每个测试用例在自己的 `project_xxx/` 子目录中运行，产物**持久保留**不删除

---

## 3. 从零创建子测试（Step-by-Step）

### 步骤 1：创建子测试目录

```bash
mkdir test/my_new_test
```

### 步骤 2：复制虚拟包到 `.lib/`

```bash
mkdir .lib
cp -r ../fixtures/* .lib/
```

如果只测试部分包，也可以只复制需要的：
```bash
mkdir .lib
cp -r ../fixtures/test@hello@1.0.0 .lib/
cp -r ../fixtures/test@world@1.0.0 .lib/
```

### 步骤 3：创建 `.data/config.json`

```json
{
    "globalLibStore": ".lib",
    "libstores": [],
    "servers": [],
    "user": "test"
}
```

- `globalLibStore: ".lib"` — 系统包存储在 `.lib/` 下（相对路径，基于 IMAKECORE_ROOT）
- `servers: []` — 不配置远程服务器（普通测试不需要下载）
- `libstores: []` — 不使用额外包存储路径

### 步骤 4：创建 `.data/packages.json`（兜底模板）

```json
{"packages": {}}
```

这是当项目目录下没有 `packages.json` 时，`AppData._loadConfig()` 会复制到项目中的模板文件。

### 步骤 5：创建 `test.py`

参见 [第 5 节](#5-编写-testpy)。

### 步骤 6：注册到 `run_all.py`

编辑 `test/run_all.py`，在 `SUITES` 列表中添加你的子测试目录名：

```python
SUITES = ["basic_resolve", "static_propagation", "validation", "my_new_test"]
```

### 步骤 7：更新 `TEST_SPEC.md`

**【强制】** 在 `test/TEST_SPEC.md` 中添加新测试目录的条目，列出所有测试函数及其说明。

### 步骤 8：创建初始 `packages.json`（可选）

如果你希望子测试有一个默认的 `packages.json`（在未通过 test.py 动态写入时使用），在子测试根目录创建：

```json
{"packages": {"test/hello": "1.0.0"}}
```

不过通常情况下，`test.py` 会通过 `_prepare()` 函数动态写入每个测试用例的 `packages.json`，所以这个文件可以不创建。

---

## 4. 创建虚拟包（Fixture）

虚拟包放在 `test/fixtures/` 下，目录命名格式为：

```
{publisher}@{name}@{version}
```

### 4.1 最小虚拟包（header-only）

```
test/fixtures/test@mylib@1.0.0/
├── package.json
└── mylib.h
```

**`package.json`**：
```json
{
    "name": "mylib",
    "version": "1.0.0",
    "publisher": "test",
    "isGlobal": true,
    "mode": "sources",
    "summary": "My test library",
    "dependencies": {}
}
```

字段说明：
| 字段 | 必填 | 说明 |
|------|------|------|
| `name` | ✅ | 包名（不含 publisher 前缀） |
| `version` | ✅ | 语义化版本，如 `1.0.0` |
| `publisher` | ✅ | 发布者名称。在 `packages.json` 中引用时用 `publisher/name` 格式 |
| `isGlobal` | ✅ | 通常为 `true`。非全局包必须有 publisher |
| `mode` | 可选 | `"sources"`（默认）、`["static"]`、`["dynamic"]` |
| `summary` | 可选 | 一句话描述 |
| `dependencies` | 可选 | 依赖声明，key 为 `publisher/name`，value 为版本约束 |

### 4.2 Source 包（含 .cpp）

在 fixture 目录中添加 `.cpp` 文件：

```
test/fixtures/test@mylib@2.0.0/
├── package.json
├── mylib.h
└── mylib.cpp
```

### 4.3 带依赖的包

```json
{
    "name": "app",
    "version": "1.0.0",
    "publisher": "test",
    "isGlobal": true,
    "mode": "sources",
    "dependencies": {
        "test/mylib": ">=1.0"
    }
}
```

### 4.4 Dynamic 包

```json
{
    "name": "dynlib",
    "version": "1.0.0",
    "publisher": "test",
    "isGlobal": true,
    "mode": ["dynamic"],
    "dependencies": {},
    "resolve": {
        "dynamicDefinition": {
            "sources": ["lib.cpp"],
            "headers": ["lib.h"]
        }
    }
}
```

**重要**：创建新 fixture 后，需要将它复制到每个子测试的 `.lib/` 目录中（或重新运行子测试的环境初始化）。

---

## 5. 编写 test.py

`test.py` 是每个子测试的核心脚本。它负责：搭建环境、运行 IMakeCore、验证产物。

### 5.1 最小模板

```python
"""
my_new_test/test.py — Self-contained functional test.

This directory IS the IMAKECORE_ROOT.
"""
import json, os, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent           # 此目录 = IMAKECORE_ROOT
IMAKECORE_PY = ROOT / ".system" / "IMakeCore.py" # IMakeCore 入口
UPDATE_DB_PY = ROOT / ".system" / "scripts" / "updateDb.py"
_PASSED = _FAILED = 0


# ═══════════════════════════════════════════════════════════════════════
# 环境搭建
# ═══════════════════════════════════════════════════════════════════════

def _setup():
    """初始化数据库：确保 .db/ 目录存在，运行 update_db.py 扫描 .lib/"""
    (ROOT / ".db").mkdir(exist_ok=True)
    subprocess.run(
        [sys.executable, "-B", str(UPDATE_DB_PY)],
        env={**os.environ, "IMAKECORE_ROOT": str(ROOT)},
        capture_output=True, text=True, check=True, timeout=60,
    )


def _run(project: Path):
    """在指定项目目录中执行 IMakeCore.py"""
    return subprocess.run(
        [sys.executable, "-B", str(IMAKECORE_PY), str(project), "qmake"],
        env={**os.environ, "IMAKECORE_ROOT": str(ROOT)},
        capture_output=True, text=True, timeout=120,
    )


def _prepare(project: Path, packages: dict) -> Path:
    """
    清理旧产物（.package.pri/.package.cmake/.package.lua, .data/, .lib/ 等），写入新的 packages.json。

    清理在【每次执行前】进行，确保每次测试从干净状态开始。
    执行完毕后文件【保留】，不删除。
    """
    for name in (".package.pri", ".package.cmake", ".package.lua", ".data", ".lib", ".support", ".bin"):
        p = project / name
        if p.exists():
            (shutil.rmtree if p.is_dir() else os.remove)(str(p))
    project.mkdir(parents=True, exist_ok=True)
    (project / "packages.json").write_text(
        json.dumps({"packages": packages}), encoding="utf-8")
    return project


# ═══════════════════════════════════════════════════════════════════════
# 断言
# ═══════════════════════════════════════════════════════════════════════

def _check(condition, msg):
    """记录一次检查结果。成功 +1，失败打印信息。"""
    global _PASSED, _FAILED
    if condition:
        _PASSED += 1
    else:
        _FAILED += 1
        print(f"  FAIL: {msg}")


# ═══════════════════════════════════════════════════════════════════════
# 测试用例
# ═══════════════════════════════════════════════════════════════════════

def test_my_first_case():
    """
    测试用例名称应清晰描述场景。

    每个测试用例有三步：
      1. _prepare() —— 创建项目目录 + 写入 packages.json
      2. _run()     —— 执行 IMakeCore.py
      3. _check()   —— 验证产物
    """
    # 步骤 1：准备
    proj = _prepare(
        ROOT / "project_my_case",       # 项目子目录名（持久保留）
        {"test/hello": "1.0.0"}         # packages.json 的内容
    )

    # 步骤 2：执行
    r = _run(proj)

    # 步骤 3：验证返回码
    _check(r.returncode == 0, f"IMakeCore 返回码={r.returncode}，预期 0")

    # 步骤 4：验证产物
    pri = proj / ".package.pri"
    _check(pri.exists(), ".package.pri 未生成")
    if pri.exists():
        _check("hello" in pri.read_text(), ".package.pri 中未找到 'hello'")


# ═══════════════════════════════════════════════════════════════════════
# 入口
# ═══════════════════════════════════════════════════════════════════════

def run():
    global _PASSED, _FAILED
    print(f"{'='*60}\nmy_new_test  (root={ROOT})\n{'='*60}")
    _setup()
    test_my_first_case()
    print(f"\n  {_PASSED} passed, {_FAILED} failed")
    return _FAILED == 0


if __name__ == "__main__":
    sys.exit(0 if run() else 1)
```

### 5.2 成功路径测试模板

验证 IMakeCore 正常运行并生成正确产物：

```python
def test_xxx():
    proj = _prepare(ROOT / "project_xxx", {"test/hello": "1.0.0"})
    r = _run(proj)
    _check(r.returncode == 0, f"rc={r.returncode}")

    # 验证 .package.pri
    pri = proj / ".package.pri"
    _check(pri.exists(), ".package.pri 不存在")
    txt = pri.read_text() if pri.exists() else ""
    _check("hello" in txt, "hello 不在 .package.pri 中")

    # 验证 include 目标文件存在
    import re
    for m in re.finditer(r'include\((.+?)\)', txt):
        _check(Path(m.group(1)).exists(), f"include 目标不存在: {m.group(1)}")

    # 验证 .lib/ 中有对应 .pri 文件
    lib = proj / ".lib"
    _check(any("hello" in p.name for p in lib.glob("*.pri")),
           ".lib/ 中没有 hello 的 .pri 文件")

    # 验证 resolve-cache.json
    cache = proj / ".data" / "resolve-cache.json"
    if cache.exists():
        data = json.loads(cache.read_text(encoding="utf-8"))
        _check("test/hello" in data.get("resolved", {}),
               "resolve-cache 中没有 test/hello")
```

### 5.3 错误路径测试模板

验证 IMakeCore 正确拒绝无效配置：

```python
def test_error_xxx():
    proj = _prepare(ROOT / "project_err_xxx",
                    {"test/hello": {"version": "1.0.0", "mode": "static"}})
    r = _run(proj)

    # 期望失败
    _check(r.returncode == 1, f"预期 exit(1)，实际 {r.returncode}")

    # 验证错误信息
    out = (r.stdout + r.stderr).lower()
    _check("header-only" in out, f"错误信息不包含 'header-only': {out[:200]}")

    # 验证【没有】生成 .package.pri
    _check(not (proj / ".package.pri").exists(),
           "错误情况下不应生成 .package.pri")
```

### 5.4 函数签名速查

| 函数 | 签名 | 说明 |
|------|------|------|
| `_setup()` | `→ None` | 初始化数据库（建目录 + 运行 update_db.py） |
| `_run(project)` | `→ CompletedProcess` | 在 project 目录中执行 IMakeCore.py |
| `_prepare(project, packages)` | `→ Path` | 清理旧产物 + 写入 packages.json，返回项目路径 |
| `_check(condition, msg)` | `→ None` | 断言，成功计数+1，失败打印 |

---

## 6. 验证模式参考

以下是可以复用的验证函数模板，根据需要复制到你的 `test.py` 中。

### 6.1 验证 `.package.pri` 存在并包含指定包名

```python
def _vfy_pri_exists(project: Path, *expected_packages: str):
    """验证 .package.pri 存在且包含所有预期包名。"""
    pri = project / ".package.pri"
    _check(pri.exists(), f"{project.name}: .package.pri 未生成")
    if not pri.exists():
        return ""
    txt = pri.read_text()
    for pkg in expected_packages:
        _check(pkg in txt, f"{project.name}: .package.pri 缺少 '{pkg}'")
    return txt
```

### 6.2 验证 include 路径对应的文件存在

```python
import re

def _vfy_pri_includes_exist(project: Path):
    """验证 .package.pri 中每个 include() 路径指向的文件真实存在。"""
    pri = project / ".package.pri"
    if not pri.exists():
        return
    for m in re.finditer(r'include\((.+?)\)', pri.read_text()):
        path = Path(m.group(1))
        _check(path.exists(),
               f"{project.name}: include 目标不存在: {path}")
```

### 6.3 验证 `.lib/` 中有对应的 `.pri` 文件

```python
def _vfy_lib_pri_exists(project: Path, *pkg_names: str):
    """验证 .lib/ 目录下存在指定包的 .pri 文件。"""
    lib = project / ".lib"
    _check(lib.exists(), f"{project.name}: .lib/ 目录未创建")
    if not lib.exists():
        return
    for name in pkg_names:
        found = any(name in p.name for p in lib.glob("*.pri"))
        _check(found, f"{project.name}: .lib/ 中缺少 '{name}' 的 .pri 文件")
```

### 6.4 验证 `resolve-cache.json`

```python
def _vfy_resolve_cache(project: Path, *pkg_names: str):
    """验证 .data/resolve-cache.json 包含解析结果。"""
    cache = project / ".data" / "resolve-cache.json"
    _check(cache.exists(), f"{project.name}: resolve-cache.json 未生成")
    if not cache.exists():
        return
    data = json.loads(cache.read_text(encoding="utf-8"))
    resolved = data.get("resolved", {})
    for name in pkg_names:
        _check(name in resolved,
               f"{project.name}: resolve-cache 缺少 '{name}'")
```

### 6.5 验证 `.package.pri` 不包含特定包（跳过/错误测试用）

```python
def _vfy_pri_absent(project: Path, *forbidden: str):
    """验证 .package.pri 中【不】包含指定包名。"""
    pri = project / ".package.pri"
    if not pri.exists():
        return
    txt = pri.read_text()
    for pkg in forbidden:
        _check(pkg not in txt,
               f"{project.name}: .package.pri 不应包含 '{pkg}'")
```

### 6.6 验证指定版本被选中

```python
def _vfy_version_selected(project: Path, version: str):
    """验证 .package.pri 中的路径包含指定版本号。"""
    pri = project / ".package.pri"
    if not pri.exists():
        _check(False, f"{project.name}: .package.pri 不存在")
        return
    txt = pri.read_text()
    _check(version in txt,
           f"{project.name}: 版本 {version} 未被选中\n{txt[:300]}")
```

### 6.7 验证旧版本没有被包含

```python
def _vfy_version_absent(project: Path, version: str):
    """验证 .package.pri 中【不】包含指定版本号。"""
    pri = project / ".package.pri"
    if not pri.exists():
        return
    _check(version not in pri.read_text(),
           f"{project.name}: 不应包含版本 {version}")
```

---

## 7. 运行测试

### 7.1 运行所有测试

```bash
cd test
python run_all.py
```

默认运行三种构建系统（qmake、cmake、xmake）；可用参数过滤，例如 `python run_all.py xmake` 只测 xmake。

输出示例：
```
============================================================
basic_resolve  (root=C:\...\test\basic_resolve)
============================================================

  37 passed, 0 failed

============================================================
TOTAL: 3 passed, 0 failed out of 3 suites
============================================================
```

### 7.2 运行单个子测试

```bash
cd test/my_new_test
python test.py
```

### 7.3 检查产物

测试执行后，每个 `project_xxx/` 子目录保留完整的生成文件：

```bash
# 查看生成的 .package.pri
cat test/basic_resolve/project_single/.package.pri

# 查看项目本地包
ls test/basic_resolve/project_single/.lib/

# 查看解析缓存
cat test/basic_resolve/project_single/.data/resolve-cache.json
```

### 7.4 调试失败的测试

```bash
cd test/my_new_test
python -c "
import subprocess, sys, os
from pathlib import Path
ROOT = Path('.').resolve()
result = subprocess.run(
    [sys.executable, '-B', str(ROOT/'.system/IMakeCore.py'),
     str(ROOT/'project_xxx'), 'qmake'],
    env={**os.environ, 'IMAKECORE_ROOT': str(ROOT)},
    capture_output=True, text=True
)
print('STDOUT:', result.stdout)
print('STDERR:', result.stderr)
print('RC:', result.returncode)
"
```

---

## 8. 添加 HTTP 下载测试

如果需要测试从 HTTP 服务器下载包的功能。

### 8.1 准备工作

```python
import shutil, tempfile
from contextlib import contextmanager
import http.server, threading

# 从 fixtures 创建 zip 包
def zip_fixture(name: str) -> Path:
    """将 test/fixtures/{name} 打包为 .zip，返回 zip 路径"""
    src = Path(__file__).resolve().parent.parent / "fixtures" / name
    tmp = Path(tempfile.mkdtemp())
    zip_base = tmp / name
    shutil.make_archive(str(zip_base), "zip", str(src))
    return Path(str(zip_base) + ".zip")

# 启动临时 HTTP 服务器
@contextmanager
def http_serve(directory: Path):
    server = http.server.HTTPServer(
        ("127.0.0.1", 0), http.server.SimpleHTTPRequestHandler)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    saved = os.getcwd()
    try:
        os.chdir(str(directory))
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        os.chdir(saved)
        server.shutdown()
```

### 8.2 编写下载测试

```python
def test_http_download():
    # 1. 打包 fixture 为 zip
    zip_path = zip_fixture("test@hello@1.0.0")

    # 2. 启动 HTTP 服务器
    with http_serve(zip_path.parent) as base_url:
        zip_url = f"{base_url}/{zip_path.name}"

        # 3. 配置 packages.json 使用 url
        proj = _prepare(ROOT / "project_download", {
            "test/hello": {
                "version": "1.0.0",
                "url": zip_url
            }
        })

        # 4. 执行
        r = _run(proj)
        _check(r.returncode == 0, f"下载失败: rc={r.returncode}")

        # 5. 验证
        _vfy_pri_exists(proj, "hello")
        _vfy_pri_includes_exist(proj)

    # with 块结束 → 服务器自动关闭
```

**注意**：下载测试需要确保 `packages.json` 使用 `"url"` 字段（而非默认的版本号字符串）。IMakeCore 会通过 `RefPackage._assemble_url()` 下载 zip、解压、注册到数据库。

---

## 9. 故障排查

### 9.1 `update_db.py` 执行失败

**症状**：测试输出 `update_db.py failed` 或 `CalledProcessError`

**排查**：
```bash
# 手动运行 update_db.py 查看完整错误
cd test/basic_resolve
set IMAKECORE_ROOT=%CD%
python -B .system/updateDb.py
```

常见原因：
- `.data/config.json` 不存在或格式错误
- `.lib/` 目录为空或包格式不正确
- Python 环境中缺少 `sqlalchemy` 包

### 9.2 `.package.pri` 未生成

**症状**：`_check` 报告 `.package.pri not generated`

**排查**：
1. 检查 IMakeCore 返回码和输出：`_check(r.returncode == 0, f"rc={r.returncode}\n{r.stdout}")`
2. 确认 `packages.json` 格式正确（key 为 `"packages"`，value 为依赖 dict）
3. 确认引用的包名与 fixture 中的 `publisher/name` 匹配
4. 确认 `.lib/` 中存在对应的 fixture 包

### 9.3 `InconsistentCandidate` 错误

**症状**：`Provided candidate ... does not satisfy ...`

**原因**：包版本约束与实际可用版本不匹配。

**排查**：
1. 检查 fixture 中实际有哪些版本：`ls .lib/ | grep 包名`
2. 检查 `packages.json` 中的版本约束是否正确
3. 确认 `update_db.py` 已执行（数据库包含最新包的索引）

### 9.4 `.system` junction 失效

**症状**：`FileNotFoundError: .system/IMakeCore.py`

**排查**：
```powershell
# 检查 junction 是否存在
cmd /c dir /aL .system

# 重新创建
rmdir .system
New-Item -ItemType Junction -Path .system -Target "..\..\..system"
```

### 9.5 测试互相干扰

**不会发生**。每个子测试是独立的 `IMAKECORE_ROOT`，：
- `.lib/` 独立（各自复制 fixtures）
- `.db/package.db` 独立（各自的 update_db.py 在各自环境中生成）
- `.data/config.json` 独立
- 测试中的项目目录 (`project_xxx/`) 在每次执行前被 `_prepare()` 清理


## 10. 测试文档同步规则（强制）

### 10.1 TEST_SPEC.md

`test/TEST_SPEC.md` 是**测试套件的唯一权威描述文件**，记录了每个子测试目录及其包含的全部测试用例。

### 10.2 修改测试时的强制规则

| 操作 | 必须同步更新的内容 |
|------|-------------------|
| 新增子测试目录 | 在 `TEST_SPEC.md` 中添加新条目，描述该目录的测试目标 |
| 在已有目录中新增测试函数 | 在 `TEST_SPEC.md` 对应条目下添加测试名称和说明 |
| 删除测试函数 | 在 `TEST_SPEC.md` 中移除对应行 |
| 修改测试函数的测试目标 | 更新 `TEST_SPEC.md` 中的描述 |
| 修改 `GUIDE.md` | 无需同步 `TEST_SPEC.md`（GUIDE 是操作指南，TEST_SPEC 是测试清单） |

### 10.3 审查流程

任何涉及测试文件的 PR 或修改，审查者必须检查：
1. `TEST_SPEC.md` 是否同步更新
2. 新增/修改的测试是否在文档中有准确描述
3. 删除的测试是否已从文档中移除


## 11. 项目文件模板 (.pro / CMakeLists.txt)

每个 `project_*/` 目录需要两个 IDE 入口文件。`.prf` / `.cmake` 通过 `isEmpty()` 判断：
- 若 `.pro` 设置了 `IMAKECORE_ROOT` → 测试项目，使用 `.pro` 的值
- 若未设置 → 真实项目，回退到系统环境变量

### 11.1 .pro 模板

```qmake
QT -= gui widgets
CONFIG += c++17 console
CONFIG -= app_bundle

SOURCES += main.cpp

# --- IMakeCore integration ---
IMAKECORE_ROOT = $$absolute_path($$PWD/../)
IMAKECORE_SYSTEM = $$(IMAKECORE_ROOT)/.system
include($$(IQMakeCore))
IQMakeCoreInit()
include($$PWD/.package.pri)
```

**变量说明：**

| 变量 | 值 | 用途 |
|------|-----|------|
| `IMAKECORE_ROOT` | `$$absolute_path($$PWD/../)` → 测试套件目录 | 测试环境（`.lib` `.data` `.db`） |
| `IMAKECORE_SYSTEM` | `$$(IMAKECORE_ROOT)/.system` → 系统环境变量的值 | 代码本体（`.system/`），所有测试项目共享 |
| `include($$(IQMakeCore))` | 系统环境变量 `IQMakeCore` | 加载 `.IMakeCore.prf` |
| `IQMakeCoreInit()` | `.prf` 中的函数 | 调用 `IMakeCore.py` 解析包 |
| `include($$PWD/.package.pri)` | 同级目录的 `.package.pri` | 包含 IMakeCore 生成的 include 链 |

**路径推导：** `project_*/` 位于 `test/<suite>/project_xxx/`，`../` 回到 `<suite>/`。

### 11.2 CMakeLists.txt 模板

```cmake
cmake_minimum_required(VERSION 3.16)
project(<name> LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 17)

add_executable(<name> main.cpp)

# --- IMakeCore integration ---
get_filename_component(TEST_ROOT "${CMAKE_CURRENT_SOURCE_DIR}/../" ABSOLUTE)
set(IMAKECORE_ROOT "${TEST_ROOT}" CACHE STRING "root" FORCE)
set(IMAKECORE_SYSTEM "$ENV{IMAKECORE_ROOT}/.system" CACHE STRING "system" FORCE)
include($ENV{ICMakeCore})
ICmakeCoreInit(<name>)
```

**变量说明：**

| 变量 | 值 | 用途 |
|------|-----|------|
| `TEST_ROOT` | `get_filename_component(.../../ ABSOLUTE)` | 测试套件绝对路径 |
| `IMAKECORE_ROOT` | `"${TEST_ROOT}" CACHE STRING "root" FORCE` | CMake cache 变量，`.prf` 读取 |
| `IMAKECORE_SYSTEM` | `"$ENV{IMAKECORE_ROOT}/.system" CACHE STRING "system" FORCE` | 系统 `.system/` 路径，所有测试共享 |
| `include($ENV{ICMakeCore})` | 系统环境变量 `ICMakeCore` | 加载 `.IMakeCore.cmake` |
| `ICmakeCoreInit(<name>)` | `.cmake` 中的函数 | 调用 `IMakeCore.py` 解析包 |

**注意：** `ICmakeCoreInit()` 内部已自动 `include(.package.cmake)`，**无需**在 CMakeLists.txt 中重复。

### 11.3 xmake.lua 模板

```lua
-- xmake.lua
-- --- IMakeCore integration ---
local imake = os.getenv("IXMakeCore")
if imake then includes(imake) end

target("<name>")
    set_kind("binary")
    add_files("main.cpp")
    add_rules("imakecore")
```

**说明：**

| 行 | 用途 |
|----|------|
| `includes(os.getenv("IXMakeCore"))` | 加载 `.IMakeCore.lua` 集成文件（定义 `imakecore` rule） |
| `target("<name>")` | 声明可执行目标，`<name>` 换成项目名 |
| `set_kind("binary")` | 目标类型为可执行程序 |
| `add_files("main.cpp")` | 编译入口源文件 |
| `add_rules("imakecore")` | 触发 `on_load`（脚本域）调用 `IMakeCore.py` 解析包并施加 include/defines/files/links |

**注意：** xmake 的 `includes()` 只在**描述作用域**可用、命令执行只在**脚本域**（`on_load`）可用，因此集成文件用 `rule("imakecore")` + `on_load` 实现；`add_rules("imakecore")` 必须放在 `target()` 块内。无需（也不能）在 xmake.lua 里调用 `imakecore_init()`。

### 11.4 main.cpp 模板

```cpp
#include "<resolved_header>.h"

int main() {
    return 0;
}
```

根据解析的包选择 include 头文件。例如 hello 包用 `"hello.h"`，world 包依赖 hello 也用 `"hello.h"`。compile 通过即可验证 IDE 环境正确。`_prepare()` 不会删除 `.pro`、`CMakeLists.txt`、`main.cpp`。

### 11.5 变量流向

```
.pro 文件                          .prf 函数 IQMakeCoreInit()
  IMAKECORE_ROOT = $$PWD/../  ─→   isEmpty(IMAKECORE_ROOT)? → FALSE → 保留 .pro 值
  IMAKECORE_SYSTEM = $$(...)/.system  →  isEmpty(IMAKECORE_SYSTEM)? → FALSE → 保留 .pro 值
                                    ↓
                                   cmd = set IMAKECORE_ROOT=... && ... python IMakeCore.py

CMakeLists.txt                     .cmake 函数 resolvePackageInfo()
  set(IMAKECORE_ROOT ... CACHE) ─→ $CACHE{IMAKECORE_ROOT} → execute_process ENV
  set(IMAKECORE_SYSTEM ... CACHE) → $CACHE{IMAKECORE_SYSTEM} → execute_process ENV
```

### 11.6 真实项目 vs 测试项目

| | 真实项目 (IPubCore) | 测试项目 (project_*) |
|--|---------------------|---------------------|
| `.pro` 是否设置 `IMAKECORE_ROOT` | ❌ | ✅ `$$absolute_path($$PWD/../)` |
| `.prf` 中 `isEmpty(IMAKECORE_ROOT)` | TRUE → 读 `$$(IMAKECORE_ROOT)` | FALSE → 保留 `.pro` 值 |
| `IMAKECORE_SYSTEM` 来源 | `$$(IMAKECORE_ROOT)/.system` | `$$(IMAKECORE_ROOT)/.system`（系统 env） |

### 11.7 预期失败项目的处理

如果一个测试项目预期会失败（如错误校验测试），应将其在 `tests.pro` 和 `CMakeLists.txt` 中**注释掉但保留**：

```qmake
# SUBDIRS += validation/project_err_static     ← 注释掉，不参与批量构建
```

```cmake
# add_subdirectory(validation/project_err_static)   ← 同上
```

**规则：**
- 写入文件，但用 `# ` 前缀注释
- IDE 批量加载时不会因失败项目中断
- 需要单独调试时取消注释即可
- 当前已注释的预期失败项目列表参见 `tests.pro` 或 `CMakeLists.txt`

### 11.8 生成规则：排除 build 目录

`tests.pro` 和 `CMakeLists.txt` 通过 glob `project_*` 自动生成。**必须排除 `build` 目录**内的匹配项——`build/` 下的 `CMakeFiles/project_*.dir` 等目录会被误匹配。

生成脚本示例（PowerShell）：
```powershell
$projects = Get-ChildItem -Recurse -Directory | Where-Object {
    $_.Name -like 'project_*' -and $_.FullName -notmatch '\\build'
}
```

手动添加新项目时也需注意此规则。


## 12. package.json 字段参考

每个包目录下必须有一个 `package.json`，描述包的元数据和构建配置。

### 12.1 基础字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `name` | string | ✅ | 包名（不含 publisher 前缀） |
| `version` | string | ✅ | 语义化版本，如 `"1.0.0"` |
| `publisher` | string | 条件 | 发布者名。`isGlobal=false` 时必须填写 |
| `isGlobal` | bool | 否 | 是否为全局包，默认 `true` |
| `mode` | string/array | 否 | 构建模式，默认 `"sources"` |
| `summary` | string | 否 | 一句话描述 |
| `dependencies` | object | 否 | 依赖声明，key=`publisher/name`，value=版本约束 |
| `autoScan` | bool | 否 | 是否自动扫描源文件，默认 `true` |
| `links` | array | 否 | 相关链接（如 GitHub） |
| `changelog` | array | 否 | 变更日志 |

**示例：**
```json
{
    "name": "mylib",
    "version": "1.0.0",
    "publisher": "example",
    "isGlobal": true,
    "mode": "sources",
    "summary": "My C++ library",
    "dependencies": {
        "test/hello": ">=1.0"
    }
}
```

### 12.2 mode 字段

| 值 | 说明 |
|----|------|
| `"sources"` / `"source"` | 源码模式（默认），直接编译进项目 |
| `"static"` | 静态库模式 |
| `"dynamic"` | 动态库模式 |
| `["source", "static"]` | 同时支持源码和静态库 |
| `["dynamic"]` | 仅动态库 |

- `"sources"` 是 `"source"` 的同义词，内部统一为 `"source"`
- 无效 mode 值会导致 `fromFolderWithJson()` 抛出 `ValueError`

### 12.3 resolve 字段

`resolve` 字段控制包的**文件扫描行为**和**编译配置**。它是一个顶层 JSON 对象，包含以下子字段：

#### 12.3.1 root — 扫描根目录

指定从哪些目录扫描源文件。默认扫描包根目录。

```json
"resolve": {
    "root": ["src", "include"]
}
```

- 字符串数组，每个元素是相对于包目录的子目录路径
- 未指定时默认使用包根目录 `["."]`
- 影响 `headers`、`sources`、`uis`、`resources` 的自动扫描范围

#### 12.3.2 headers — 显式头文件列表

手动指定头文件，覆盖自动扫描。

```json
"resolve": {
    "headers": ["inc/header1.h", "inc/header2.h"]
}
```

- 字符串数组，相对于包根目录的路径
- 若指定则**跳过**自动扫描头文件
- 支持绝对路径

#### 12.3.3 sources — 显式源文件列表

手动指定源文件，覆盖自动扫描。

```json
"resolve": {
    "sources": ["src/impl1.cpp", "src/impl2.cpp"]
}
```

- 字符串数组，相对于包根目录的路径
- 若指定则**跳过**自动扫描源文件

#### 12.3.4 includePaths — 包含路径

指定编译器的 include 搜索路径。影响 `.pri`/`.cmake` 中生成的 `INCLUDEPATH`。

```json
"resolve": {
    "includePaths": ["inc", "thirdparty/inc"]
}
```

- 若指定了 `root`，默认使用 root 目录作为 include 路径
- 若未指定 `root` 且未指定 `includePaths`，默认使用包根目录

#### 12.3.5 definitions — 预处理器定义

指定编译时的预处理器宏定义。

```json
"resolve": {
    "definitions": ["USE_FEATURE_X", "VERSION=1"]
}
```

- 字符串数组，格式为 `"NAME"` 或 `"NAME=VALUE"`
- 写入 `.pri` 的 `DEFINES` 和 `.cmake` 的 `target_compile_definitions`

#### 12.3.6 precompileHeaders — 预编译头

指定预编译头文件列表。

```json
"resolve": {
    "precompileHeaders": ["pch.h", "stable.h"]
}
```

- 字符串数组，相对于包根目录的路径
- 写入 `.pri` 的 `PRECOMPILED_HEADER` 配置

#### 12.3.7 dynamicDefinition — 动态库定义

当 `mode` 包含 `"dynamic"` 时，必须声明动态库的源文件和头文件。

```json
{
    "mode": ["dynamic"],
    "resolve": {
        "dynamicDefinition": {
            "sources": ["lib.cpp", "impl.cpp"],
            "headers": ["lib.h", "export.h"]
        }
    }
}
```

- `sources`：动态库包含的源文件
- `headers`：动态库导出的头文件
- 若 `mode=dynamic` 但未定义 `dynamicDefinition`，运行时会报错

#### 12.3.8 ignore — 文件忽略模式

指定扫描时要忽略的文件/目录。

```json
"resolve": {
    "ignore": [".git", "*.tmp", "test/"]
}
```

- 字符串数组，支持 gitignore 风格的 glob 模式
- 应用于自动扫描的文件过滤

### 12.4 验证规则

| 规则 | 触发条件 |
|------|---------|
| `name` 和 `version` 必填 | `fromFolderWithJson()` |
| `isGlobal=false` 时 `publisher` 必填 | `fromFolderWithJson()` |
| `mode` 必须是有效值 | `fromFolderWithJson()` → `ValueError` |
| `origin` 必须是 `"local"` 或 `"default"` | `RefPackage.from_package_json()` |
| `path`/`url`/`git` 互斥 | `RefPackage._from_dict_entry()` |
| `dynamicDefinition` 必须有 `sources` 和 `headers` | 运行时校验 |
| `updateDb.py` 遇到无效 `package.json` 时跳过并 `[WARN]` | `_index_package()` |

