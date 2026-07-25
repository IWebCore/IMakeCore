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

**IDE 使用**：用 Qt Creator 打开 `test/tests.pro` 或 `test/CMakeLists.txt`，即可将所有 35 个测试项目导入 IDE。
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
    清理旧产物（.package.pri, .data/, .lib/ 等），写入新的 packages.json。

    清理在【每次执行前】进行，确保每次测试从干净状态开始。
    执行完毕后文件【保留】，不删除。
    """
    for name in (".package.pri", ".package.cmake", ".data", ".lib", ".support", ".bin"):
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
