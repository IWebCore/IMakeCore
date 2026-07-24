# IMakeCore 功能测试指南

## 快速开始

```bash
# 运行全部测试
cd test && python run_all.py

# 运行单个子测试
cd test/basic_resolve && python test.py
cd test/static_propagation && python test.py
cd test/validation && python test.py
```

## 目录结构

```
test/
├── run_all.py                   # 主运行器（串联所有子测试）
├── GUIDE.md                     # 本文档
├── fixtures/                    # 共享虚拟包模板
│   ├── test@hello@1.0.0/        # 格式: {publisher}@{name}@{version}
│   ├── test@hello@2.0.0/
│   ├── test@world@1.0.0/
│   └── test@dynamic_lib@1.0.0/
├── basic_resolve/
│   ├── test.py                  # 自包含测试脚本
│   └── packages.json            # 测试场景的包声明
├── static_propagation/
│   ├── test.py
│   └── packages.json
└── validation/
    ├── test.py
    └── packages.json
```

## 每个 test.py 的自动化流程

每个子测试的 `test.py` 是自包含的，执行时：

```
1. 创建临时 IMAKECORE_ROOT/
   ├── .system/          ← 从项目根复制代码本体
   ├── .lib/             ← 从 fixtures/ 复制虚拟包
   ├── .data/
   │   ├── config.json   ← 自动生成（globalLibStore=.lib）
   │   └── packages.json ← 空模板
   └── .db/
       └── package.db    ← update_db.py 自动生成

2. 设置环境变量 IMAKECORE_ROOT = 临时目录

3. 运行 update_db.py → 扫描 .lib/ → 生成 .db/package.db

4. 为每个测试用例创建临时项目目录，写入 packages.json

5. 运行 IMakeCore.py 解析包

6. 验证产物（.package.pri 是否存在、内容是否正确）

7. 清理临时文件
```

## 如何添加新的虚拟包

在 `test/fixtures/` 下创建目录，命名格式 `{publisher}@{name}@{version}`：

```
fixtures/test@mylib@1.0.0/
├── package.json       # 必须
└── mylib.h            # 可选（决定 header-only vs source）
```

`package.json` 模板：
```json
{
    "name": "mylib",
    "version": "1.0.0",
    "publisher": "test",
    "isGlobal": true,
    "mode": "sources",
    "dependencies": {}
}
```

## 如何添加新的子测试

1. 创建目录 `test/my_feature/`
2. 创建 `packages.json`（定义测试场景需要的包声明）
3. 创建 `test.py`（参考 `basic_resolve/test.py` 的结构）
4. 在 `test/run_all.py` 的 `SUITES` 列表中添加 `"my_feature"`

`test.py` 最小模板：
```python
import json, os, shutil, subprocess, sys, tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures"
TEST_DIR = Path(__file__).resolve().parent
SYSTEM_SRC = PROJECT_ROOT / ".system"
_PASSED = _FAILED = 0

def _setup_root(): ...
def _run_update_db(root): ...
def _run_imakecore(root, project): ...

def test_my_scenario(root):
    proj = Path(tempfile.mkdtemp(dir=TEST_DIR, prefix="proj_"))
    (proj / ".data").mkdir()
    (proj / "packages.json").write_text(
        json.dumps({"packages": {"test/hello": "1.0.0"}}))
    result = _run_imakecore(root, proj)
    assert result.returncode == 0
    shutil.rmtree(proj, ignore_errors=True)

def run():
    root = _setup_root()
    try:
        _run_update_db(root)
        test_my_scenario(root)
    finally:
        shutil.rmtree(root, ignore_errors=True)

if __name__ == "__main__":
    run()
```

## 隔离原理

- 每个 `test.py` 创建独立的临时 `IMAKECORE_ROOT`
- `.db/package.db` 在临时目录下生成，不污染真实环境
- `.lib/` 从 `fixtures/` 复制，每次测试都是全新副本
- 测试完成后自动清理临时目录
- 环境变量仅在 subprocess 中设置，不影响父进程

## 调试

```bash
# 查看 IMakeCore 的完整输出
cd test/basic_resolve
python -c "
import subprocess, sys, os, tempfile
from pathlib import Path
# ... 手动执行 _run_imakecore 并打印 stdout/stderr
"
```
