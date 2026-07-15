# IMakeCore 包解析推导引擎 — 设计文档

> 日期: 2026-07-05 | 状态: 设计定稿

---

## 1. 问题定义

### 1.1 当前解析流程的局限

当前的 `PackageResolver` 执行简单的 1:1 匹配：`RefPackage` → `LibPackage`。它不处理：

- **版本冲突**：当两个包依赖同一库的不同版本时，不会尝试调解
- **传递依赖递归**：`_resolve_external_deps` 只会添加直接依赖，不会系统性搜索所有可能的版本组合
- **mode 分支**：一个库可以同时以 static/source 方式存在，但当前只匹配一个结果
- **动态库依赖隔离**：动态库的依赖不应该泄漏到主命名空间中

### 1.2 目标

设计一个**推导引擎**，通过"虚拟环境迭代"的方式，系统性解决包解析的版本冲突和 mode 分支问题。

---

## 2. 核心概念

### 2.1 RefPackage — 用户声明

```
RefPackage
├── name: str
├── version_range: SpecifierSet      # 用户声明的版本范围
├── mode: "source" | "static" | "dynamic" | "default"
├── fixedPath: str | None            # 如果指定，version 是确定的
├── publisher: str
└── origin: "local" | "system" | "default"
```

`refPackage` 列表是推导的基础。所有后续推导都以此为根。

### 2.2 InferPackage — 推导中的包

```
InferPackage
├── id: int                          # 唯一标识，只增不减
├── inferId: int                     # 指向来源 InferPackage (0 = 来自 RefPackage)
├── publisher: str
├── name: str
├── mode: "source" | "static" | "dynamic"
├── key: str                         # publisher/name:mode（唯一索引）
│
├── currentSelectedPackage
│   ├── version: str                 # 当前选中的版本
│   └── dependencies: list[Dependency]  # 该版本的依赖
│
├── availablePackages: list[LibPackage]  # 所有满足 name 的包
├── restrictions: list[Restriction]      # 版本限制
│
└── allPackages: dict[str, list[LibPackage]]  # 全局包索引 (缓存)
```

#### mode 与 key 的关系

一个 InferPackage 的 `key = publisher/name:mode`。同一个库的三种 mode 被视为三个不同的 InferPackage：

```
ICore:source  → key = "yuekeyuan/ICore:source"
ICore:static  → key = "yuekeyuan/ICore:static"
ICore:dynamic → key = "yuekeyuan/ICore:dynamic"
```

这允许同一个库以不同 mode 存在于不同位置（例如：主项目以 source 引用，子项目以 static 引用）。

### 2.3 Restriction — 版本限制

```
Restriction
├── inferId: int                     # 来源推断的 ID
├── from_key: str                    # 来源包的 key
├── name: str                        # 限制的库名
├── version_range: SpecifierSet      # 要求的版本范围
└── level: int                       # 距离根的距离 (根 = 0)
```

每当一个 inferPackage 依赖另一个包时，就创建一个 Restriction。

### 2.4 InferPackageEnv — 推导环境

```
InferPackageEnv
├── infer_packages: dict[str, InferPackage]  # key → InferPackage
├── ref_packages: list[RefPackage]           # 原始用户声明
└── dependency_type: DependencyType           # STATIC_EXPORT / DYNAMIC_ISOLATED
```

**核心能力**：InferPackageEnv 可以**完整复制**。这意味着我们可以创建一个副本进行"试错"。

```
env2 = env.clone()
env2.resolve()
if env2.is_resolved():
    env = env2
else:
    # 放弃副本，保留原 env
```

---

## 3. 推导算法

### Step 1: RefPackage → InferPackage

```
输入: refPackageList
输出: InferPackageEnv (infer_packages 已填充，未解析)

for each ref in refPackageList:
    infer = InferPackage()
    infer.id = next_id++
    infer.inferId = 0               # 0 = 来自 RefPackage
    infer.name = ref.name
    infer.publisher = ref.publisher
    infer.mode = infer_initial_mode(ref)
    infer.key = f"{ref.publisher}/{ref.name}:{infer.mode}"
    
    infer.allPackages = query_all_packages(env)
    infer.availablePackages = filter_by_name_and_publisher(infer.allPackages, key)
    
    if ref.fixedPath:
        infer.currentSelectedPackage = load_from_fixed_path(ref.fixedPath)
    else:
        infer.restrictions.append(Restriction(
            inferId=0, from_key=infer.key, name=infer.name,
            version_range=ref.version_range, level=0
        ))
    
    env.infer_packages[infer.key] = infer
```

#### mode 初始推导规则

```
def infer_initial_mode(ref):
    if ref.mode != "default": return ref.mode
    detail = ref.real_package.getDetail()
    if detail is None or detail.is_header_only(): return "source"
    supported = getattr(ref.real_package, "_supported_modes", ["source","static"])
    if "static" in supported: return "static"    # 默认静态编译
    return "source"
```

### Step 2: 选取版本

```
for each infer in env.infer_packages.values():
    available = infer.availablePackages
    for restr in infer.restrictions:
        available = [p for p in available if restr.version_range.contains(Version(p.version))]
    if not available:
        raise UnsolvableError(f"{infer.key}: no version satisfies restrictions")
    selected = min(available, key=lambda p: Version(p.version))  # 最小版本
    infer.currentSelectedPackage = {
        "version": selected.version,
        "dependencies": parse_dependencies(selected)
    }
```

选择最小版本：最小版本引入的变更最少。

### Step 3: 传播依赖

```
for each infer in env.infer_packages.values():
    if infer.mode == "dynamic": continue  # 动态库依赖隔离
    
    for each dep in infer.currentSelectedPackage.dependencies:
        dep_key = f"{publisher}/{dep.fullName}:{infer.mode}"
        if dep_key not in env.infer_packages:
            target = InferPackage(..., depends_on=infer)
            env.infer_packages[dep_key] = target
        
        target.restrictions.append(Restriction(
            inferId=infer.id, from_key=infer.key,
            name=dep.fullName, version_range=dep.versionSpec,
            level=infer.level + 1
        ))
```

#### 动态库依赖隔离

**核心规则**：动态库的依赖不导出到主命名空间。动态库在子环境中独立解析。

```
if infer.mode == "dynamic":
    sub_env = InferPackageEnv()
    sub_env.infer_packages = ...  # 在子环境中解析
    continue  # 依赖不添加到全局 restrictions
```

### Step 4: 广度优先调解

```
max_iterations = 100
iteration = 0

while True:
    iteration += 1
    if iteration > max_iterations:
        raise UnsolvableError("too many iterations: circular dependency?")
    
    changed = False
    for infer in env.infer_packages.values():
        available = infer.availablePackages
        for restr in infer.restrictions:
            available = [p for p in available if restr.version_range.contains(Version(p.version))]
        if not available:
            raise UnsolvableError(f"{infer.key}: no version")
        
        best = min(available, key=lambda p: Version(p.version))
        if best.version != infer.currentSelectedPackage.get("version"):
            infer.currentSelectedPackage = {
                "version": best.version,
                "dependencies": parse_dependencies(best)
            }
            changed = True
    
    if not changed:
        break  # 所有包满足 → 解析完成
```

---

## 4. AutoLoadSubPackage

### 4.1 定义

```python
class RefPackage:
    auto_load_sub_package: bool = True  # 默认自动加载子包
```

**True**：用户只需声明自己的包，子包自动解析。
**False**：用户必须显式声明所有包，缺少依赖报错。

### 4.2 对推导的影响

```
auto_load_sub_package = True:
    Step 3 传播依赖时自动添加所有子依赖

auto_load_sub_package = False:
    只处理用户显式声明的 RefPackage
    缺少依赖报错
```

---

## 5. package.lock 文件

### 5.1 结构

```json
{
    "version": 1,
    "resolved": {
        "yuekeyuan/ICore:source": {
            "version": "1.1.0",
            "mode": "source",
            "path": "C:/.../.lib/yuekeyuan@ICore@1.1.0",
            "dependencies": {"nlohmann.json": "*"}
        }
    }
}
```

### 5.2 生成

推导完成后序列化：

```python
lock = {"version": 1, "resolved": {}}
for key, infer in env.infer_packages.items():
    if infer.currentSelectedPackage:
        lock["resolved"][key] = {
            "version": infer.currentSelectedPackage["version"],
            "mode": infer.mode,
            "path": resolve_path(infer),
            "dependencies": infer.currentSelectedPackage.get("dependencies", {})
        }
```

---

## 6. 与当前系统的关系

### 6.1 当前问题

| 问题 | 当前 | 新设计 |
|------|------|--------|
| 版本冲突 | 无处理，报错 | 广度优先迭代调解 |
| 传递依赖 | 只加一层 | 递归传播 + 约束求解 |
| mode 分支 | 1:1 匹配 | 3 mode 独立 InferPackage |
| 动态库隔离 | 无 | 动态库边界停止传播 |
| 试错/回滚 | 无 | clone() 支持 |

### 6.2 集成路径

```
Phase 1: 并行运行，比较结果
Phase 2: 替换 resolve_all
Phase 3: 写入 package.lock
```

---

## 7. 待定项

| # | 问题 | 建议 |
|---|------|------|
| 1 | 最小版本选择？ | 最小变化原则 |
| 2 | 动态库依赖隔离方式？ | 子环境独立解析 |
| 3 | mode 分支独立？ | 3 种 mode 独立 InferPackage |
| 4 | clone 深拷贝效率？ | 包数量<100，可接受 |
