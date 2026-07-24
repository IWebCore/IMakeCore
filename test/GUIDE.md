# IMakeCore 功能测试指南

## 快速开始

```bash
# 安装依赖
pip install pytest

# 运行全部测试
pytest test/ -v

# 运行单个测试文件
pytest test/test_basic_resolve.py -v

# 运行特定测试
pytest test/test_basic_resolve.py::test_single_package_no_deps -v
```

## 架构总览

```
pytest test/ -v
  │
  └─ conftest.py (session scope, 仅一次)
       ├── 创建临时 IMAKECORE_ROOT
       ├── 复制 .system/ 代码本体
       ├── 复制 fixtures/ → .lib/ (虚拟包)
       ├── 写入 .data/config.json (最小配置)
       ├── 设置环境变量 IMAKECORE_ROOT
       ├── 调用 update_db.py → 建表 + 索引
       └── 就绪，可供所有测试使用

  每个测试函数:
       ├── conftest 提供 test_env (共享环境) + test_project (独立项目目录)
       ├── 写入 packages.json
       ├── helpers.run_imakecore() → subprocess 调用 IMakeCore.py
       ├── helpers.assert_xxx() → 验证产物
       └── tmp_path 自动清理
```

## 目录结构

```
test/
├── GUIDE.md                    ← 本文档
├── conftest.py                 ← 全局环境搭建 (pytest fixtures)
├── helpers.py                  ← 共享工具函数
├── fixtures/                   ← 虚拟包模板
│   ├── hello@1.0.0/            # 格式: {publisher}@{name}@{version}
│   ├── hello@2.0.0/
│   ├── world@1.0.0/
│   └── dynamic_lib@1.0.0/
├── test_basic_resolve.py       ← 测试文件 ...
├── test_static_propagation.py
├── test_validation.py
└── test_download.py
```

## 如何添加新的虚拟包 (fixture)

1. 在 `test/fixtures/` 下创建目录，命名格式 `{publisher}@{name}@{version}`

2. 在目录中创建 `package.json`:
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

3. 根据需要添加源码文件:
   - 只有 `.h` 文件 → header-only 包
   - 有 `.cpp` 文件 → source 包
   - `mode: "dynamic"` + resolve → 动态库

4. 运行测试 — conftest.py 会自动复制新 fixture 并重建数据库。

## 如何编写新测试

### 最小模板

```python
def test_my_scenario(test_env, test_project):
    """一句话描述测试目标。"""
    # 1. 配置 packages.json
    write_packages_json(test_project, {"test/hello": "1.0.0"})

    # 2. 执行 IMakeCore
    result = run_imakecore(test_project)

    # 3. 断言
    assert result.returncode == 0
    assert (test_project / ".package.pri").exists()
```

### 期望错误的测试

```python
def test_error_scenario(test_env, test_project):
    """验证特定错误被正确捕获。"""
    write_packages_json(test_project, {"test/hello": {"version": "1.0.0", "mode": "static"}})

    result = run_imakecore(test_project)
    assert result.returncode == 1
    assert "header-only" in result.stderr
```

### 高级配置

```python
def test_dict_config(test_env, test_project):
    write_packages_json(test_project, {
        "test/hello": {
            "version": ">=1.0",
            "mode": "static",
            "origin": "local"
        }
    })
```

## helpers.py API

| 函数 | 用途 |
|------|------|
| `write_packages_json(project, deps)` | 写入 packages.json |
| `run_imakecore(project, pack_type="qmake")` | subprocess 调用 IMakeCore.py，返回 CompletedProcess |
| `run_update_db(root_path)` | subprocess 调用 update_db.py |
| `assert_pri_contains(project, text)` | 断言 .package.pri 包含指定文本 |
| `assert_file_exists(project, filename)` | 断言产物文件存在 |
| `zip_fixture(name)` | 打包 fixture 为 .zip，返回路径 |
| `http_serve(directory)` | 上下文管理器：启动 HTTP 服务器 → yield url |

## conftest.py fixtures

| fixture | scope | 用途 |
|---------|-------|------|
| `test_env` | session | 全局隔离环境（IMAKECORE_ROOT, DB, fixtures） |
| `test_project` | function | 每个测试独立的项目目录 |

## 隔离原理

每次 `run_imakecore()` 启动新的子进程，拥有:
- 独立的 Python 解释器 → `models._engine` 单例独立
- 独立的 `IMAKECORE_ROOT` 环境变量 → 所有路径指向 tmp
- 独立的文件系统 (tmp_path) → 无交叉污染

## 常见问题

**Q: 为什么用 subprocess 而不是直接 import？**
A: `models.py` 的 `_engine` 是模块级单例。直接 import 会导致所有测试共享同一个 SQLite 连接。subprocess 保证每次调用完全隔离。

**Q: 如何调试失败的测试？**
```bash
pytest test/test_basic_resolve.py::test_single_package_no_deps -v -s
```
`-s` 输出 subprocess 的 stdout/stderr。

**Q: 如何只运行特定测试？**
```bash
pytest test/ -k "static"
```

**Q: 如何添加需要 HTTP 下载的测试？**
参见 `test_download.py` 示例。核心模式:
```python
def test_http_download(test_env, test_project):
    zip_path = zip_fixture("hello@1.0.0")
    with http_serve(os.path.dirname(zip_path)) as url:
        write_packages_json(test_project, {
            "test/hello": {"version": "1.0.0", "url": f"{url}/hello@1.0.0.zip"}
        })
        result = run_imakecore(test_project)
        assert result.returncode == 0
```
