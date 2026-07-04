# IMakeCore 重构详细计划

> 日期: 2026-07-03 | 状态: 计划阶段

---

## 0. 为什么重构：当前代码全景分析

### 0.1 当前调用链跟踪

用户项目中的 `.pro` 文件通过 `ipc init` 被插入了三行代码，之后 qmake 执行时会触发完整的包解析链：

```
qmake 执行用户的 .pro 文件
  │
  include($$(IQMakeCore))        ← 展开为 %IMAKECORE_ROOT%/.system/.IMakeCore.prf
  │                                   声明 IQMakeCoreInit() 定义
  │
  IQMakeCoreInit()               ← qmake 调用 Python 引擎
  │   cmd = "python -B IMakeCore.py <项目目录> qmake"
  │   res = system(cmd)
  │   if result != 0: error("packages configuration failed")
  │
  └── Python 引擎启动 ──────────────────────────────
        │
        appPath = sys.argv[1]              # 项目路径, 如 "E:/Ecs"
        packType = sys.argv[2]             # "qmake" 或 "cmake"
        │
        env = EnvConfig(appPath, packType) # ① 构建运行环境
        │   └── EnvConfig.__init__() 内部:
        │       self.sysPath = os.getenv("IMAKECORE_ROOT")
        │       _global = GlobalData()      # 读 .data/config.json
        │       self.sysLibStore = _global.get_sys_lib_store()  # 系统包目录
        │       self.libstores = _global.get_libstores()        # 所有包目录
        │       self.servers = _global.get_servers()            # 下载服务器
        │       self.libs : dict[str, list[LibPackage]] = {}
        │       loadAppConfig()            # 追加项目 .lib/ 到 libstores
        │       checkDirectoryExists()     # 创建缺失目录
        │       parseLibs()                # ← 关键: 从 package.db 加载包索引
        │           │
        │           │  session = get_session()
        │           │  rows = session.query(LibPackageTable).all()
        │           │  for row in rows:
        │           │      lib = LibPackage.from_db_row(row)
        │           │      if lib.publisher == "": lib.publisher = self.userName
        │           │      key = lib.publisher + "/" + lib.name
        │           │      self.libs[key].append(lib)
        │           │  # 结果: self.libs = {"yuekeyuan/ICore": [LibPackage(v1.1.0), ...]}
        │           │
        │           │  ⚠️ 问题: 只查 DB, 项目 .lib/ 下的包不在 self.libs 中
        │
        app = AppConfig(appPath)           # ② 读项目 packages.json
        │   └── AppConfig.__init__() 内部:
        │       jsonPath = os.path.join(path, "packages.json")
        │       if not exists(jsonPath):
        │           从 IMAKECORE_ROOT/.data/packages.json 复制模板
        │       self.json = Utils.loadJson(jsonPath)
        │       self.forceLocal = self.json.get("forceLocal", False)  # 全局 bool
        │       self.packages : list[AppPackage] = []
        │       loadPackages()
        │           for key, value in self.json["packages"].items():
        │               if isinstance(value, str):
        │                   pkg = AppPackage.fromNameVersion(key, value, self.forceLocal)
        │               elif isinstance(value, dict):
        │                   pkg = AppPackage.fromNameConfig(key, value, self.forceLocal)
        │               if not pkg.skip: self.packages.append(pkg)
        │
        loadPackages(app, env)             # ③ 逐个解析包
        │   for package in app.packages:
        │       success = LocatePackages(package, env).success
        │       if not success:
        │           success = DownloadPackage(package, env).success
        │       if not success:
        │           error(f"Failed to locate or download: {package.name}")
        │           exit(1)
        │
        │   LocatePackages 内部:
        │       if package.path.strip() != '':
        │           lib = LibPackage(package.path)     # 从磁盘读 package.json
        │           if lib.isMatch(package):
        │               package.libPackage = lib        # 绑定匹配的包
        │               return True
        │           else:
        │               error("not found in user defined path")  # ← 直接 exit!
        │               exit(1)
        │       # name 精确匹配
        │       if package.name in self.env.libs:
        │           for lib in self.env.libs[package.name]:      # 按版本降序遍历
        │               if lib.isMatch(package):
        │                   package.libPackage = lib
        │                   return True
        │           return False  # 精确 key 存在但版本不匹配 → 不继续查找
        │       # name 模糊匹配 (跨 publisher)
        │       for key in self.env.libs.keys():
        │           if key.endswith(package.name):
        │               for lib in self.env.libs[key]:
        │                   if lib.isMatch(package):
        │                       package.libPackage = lib
        │                       return True
        │       return False
        │
        │   DownloadPackage 内部:
        │       self.cachePath = env.sysCachePath / "{name}_{timestamp}.zip"
        │       # 尝试下载
        │       if package.urls:
        │           downloadByUrl(package.urls)   # GET 每个 URL
        │       else:
        │           downloadByServer()            # GET /package/download?name=&version=
        │       # 解压到 sysLibStore
        │       libPath = sysLibStore / "{publisher}@{name}@{version}"
        │       zipfile.extractall(libPath)
        │       # 验证
        │       lib = LibPackage(libPath)
        │       if lib.isMatch(package):
        │           package.libPackage = lib
        │           return True
        │       ⚠️ 问题: 下载成功但不写入 package.db!
        │
        MakeUtils.updatePackageForceLocal(app.packages, env)  # ④ forceLocal 复制
        │   for package in app.packages:
        │       if package.forceLocal:
        │           newPath = appLibStore / "{publisher}@{name}@{version}"
        │           shutil.copytree(package.path, newPath)
        │           package.path = newPath
        │           package.libPackage.path = newPath
        │       ⚠️ 问题: DB 中的路径是旧的绝对路径, 生成时需要 remap (BUG-1)
        │
        MakeUtils.checkPackageDependencies(app.packages)      # ⑤ 验证传递依赖
        │   for lib in app.packages:
        │       for dep in lib.libPackage.dependencies:
        │           遍历所有 lib2: 检查 dep.matchLib(lib2.libPackage)
        │           找不到: error + exit(1)
        │       ⚠️ 问题: 只验证不自动添加, 用户必须手动列出所有传递依赖
        │
        MakeUtils.createDumpJson(app.packages, env)            # ⑥ 导出调试
        MakeUtils.createIncludeFile(packType, app.packages, env)  # ⑦ 生成构建文件
```

### 0.2 核心问题清单

以上调用链中标注的 ⚠️ 问题：

| # | 位置 | 问题 | 影响 | 严重度 |
|---|------|------|------|--------|
| **P1** | `AppConfig.py:19` | `forceLocal` 是全局 bool | 不能在同一项目中混合"强制本地"和"允许系统"的包 | HIGH |
| **P2** | `AppPackage.py:10-11` | `path` 和 `urls` 是并列字段, 同时存在无定义 | LocatePackage 先检查 path, 失败后 exit, 不会走到 DownloadPackage | MED |
| **P3** | `DownloadPackage.py:26-27` | 下载成功后不写 DB | 下次 EnvConfig.parseLibs() 看不到包, 重复下载或失败 | HIGH |
| **P4** | `EnvConfig.py:75` | `parseLibs()` 只查 DB | 项目 .lib/ 下的包在索引中不可见 | HIGH |
| **P5** | `EnvConfig.py:100` | `lib.publisher = "" → 改为 self.userName` | 后续 `_get_detail_from_db(group=userName)` 查不到 DB 中 `group=""` 的记录 | MED |
| **P6** | 无 | 不支持 git 下载 | 用户只能通过 URL zip 获取第三方包 | MED |
| **P7** | 无 | 无解析缓存 | 每次 qmake/cmake 都全量解析, 即使包未变化 | LOW |

### 0.3 重构思路总览

```
当前:
  packages.json → AppConfig → AppPackage[] → LocatePackage / DownloadPackage → 手动 forceLocal → 生成

目标:
  packages.json → AppData → RefPackage[] → PackageResolver (统一解析: 缓存/path/origin/下载)
                                           → 自动 external_package (传递依赖)
                                           → 生成
```

核心变化:
1. `AppConfig` → `AppData`: 增加 `origin` 字段, 增加 `external_packages`, 增加缓存读写
2. `AppPackage` → `RefPackage`: 清晰的"意图声明"对象, 移除 forceLocal, 增加 git + resolve
3. `LocatePackage` + `DownloadPackage` → `PackageResolver`: 统一 path/origin/下载流程
4. 新增 `scripts/util/download/`: BaseDownloader + Url + Git 下载器
5. 新增 `resolve-cache.json`: 缓存解析结果, 惰性更新策略

---

## 1. AppData — 替代 AppConfig

### 1.1 文件位置

`scripts/data/AppData.py`

### 1.2 与 AppConfig 的差异

| 方面 | AppConfig (当前) | AppData (目标) |
|------|-----------------|---------------|
| 配置文件 | packages.json | packages.json (新格式) |
| 包来源策略 | `forceLocal` 全局 bool | `origin`: 全局 + 每个包独立 |
| 包对象 | `list[AppPackage]` | `list[RefPackage]` |
| 外部包 | 无 | `list[RefPackage]` (传递依赖自动添加) |
| 缓存 | 无 | `resolve-cache.json` 读写 |

### 1.3 完整的 __init__ 流程

```python
class AppData:
    def __init__(self, project_path: str):
        self.path = project_path
        
        # ====== Step 1: 加载 packages.json ======
        json_path = os.path.join(self.path, "packages.json")
        if not os.path.exists(json_path):
            src = os.path.join(os.getenv("IMAKECORE_ROOT"), ".data", "packages.json")
            shutil.copyfile(src, json_path)
        
        self.json = Utils.loadJson(json_path)
        
        # ====== Step 2: 读取全局 origin (向后兼容 forceLocal) ======
        if "origin" in self.json:
            self.global_origin = self.json["origin"]
        elif self.json.get("forceLocal", False):
            print("WARNING: 'forceLocal' is deprecated, use 'origin: local'")
            self.global_origin = "local"
        else:
            self.global_origin = "default"
        
        if self.global_origin not in ("local", "system", "default"):
            print(f"ERROR: Invalid global origin '{self.global_origin}'."
                  f" Must be local, system, or default.")
            exit(1)
        
        # ====== Step 3: 读取 localLibStore ======
        self.local_lib_store = self.json.get("localLibStore")
        if self.local_lib_store is None:
            self.local_lib_store = os.path.join(self.path, ".lib")
        elif not os.path.isabs(self.local_lib_store):
            self.local_lib_store = os.path.join(self.path, self.local_lib_store)
        self.local_lib_store = os.path.normpath(self.local_lib_store)
        
        # ====== Step 4: 解析 packages → RefPackage 列表 ======
        self.packages: list[RefPackage] = []
        self.external_packages: list[RefPackage] = []
        self._parse_packages()
        
        # ====== Step 5: 加载缓存 ======
        self.cache_path = os.path.join(self.path, ".data", "resolve-cache.json")
        self.cache = {}
        self._load_cache()
    
    def all_packages(self) -> list[RefPackage]:
        """返回所有包 (含传递依赖)"""
        return self.packages + self.external_packages
```

### 1.4 _parse_packages() — 三分支解析

```python
def _parse_packages(self):
    raw = self.json.get("packages", {})
    if not raw:
        print("ERROR: packages.json does not contain 'packages' field.")
        print("       Expected format: {'packages': {'name': 'version', ...}}")
        exit(1)
    
    for name, value in raw.items():
        ref = self._parse_one(name, value)
        if ref is not None:   # version == "x" 时返回 None
            self.packages.append(ref)

def _parse_one(self, name: str, value) -> RefPackage | None:
    
    # ═══════════════════════════════════════════
    # 分支 A: value 是字符串
    # 格式: "ICore": "*" 或 "ICore": ">=1.0"
    # ═══════════════════════════════════════════
    if isinstance(value, str):
        version = value.strip()
        if version == "x":
            return None   # skip
        
        ref = RefPackage()
        ref.name = name
        ref.version = version
        ref.version_range = Utils.parseVersionSpecifier(version)
        ref.origin = self.global_origin
        ref.publisher = ""          # 不限制 publisher
        # path, url, git, resolve 保持 None — 纯名称匹配
        return ref
    
    # ═══════════════════════════════════════════
    # 分支 B: value 是 dict
    # 格式: "nlohmann.json": {"version": ">=3.0", "url": "...", "origin": "system"}
    # ═══════════════════════════════════════════
    if isinstance(value, dict):
        config = value
        
        # B1: version
        version = config.get("version", "*").strip()
        if version == "x":
            return None
        
        ref = RefPackage()
        ref.name = name
        ref.version = version
        ref.version_range = Utils.parseVersionSpecifier(version)
        
        # B2: publisher
        ref.publisher = config.get("publisher", "")
        ref.is_global = config.get("isGlobal", True)
        
        # B3: origin (包级覆盖全局)
        if "origin" in config:
            ref.origin = config["origin"]
            if ref.origin not in ("local", "system", "default"):
                print(f"ERROR: Package '{name}' has invalid origin '{ref.origin}'."
                      f" Must be one of: local, system, default.")
                exit(1)
        else:
            ref.origin = self.global_origin
        
        # B4: 来源字段互斥检查
        has_path = "path" in config
        has_url  = "url" in config
        has_git  = "git" in config
        count = sum([has_path, has_url, has_git])
        
        if count > 1:
            print(f"ERROR: Package '{name}' has multiple source fields."
                  f" path, url, and git are mutually exclusive.")
            exit(1)
        
        if has_path:
            ref.path = config["path"]
            # 路径解析延迟到 PackageResolver (需要 project_path)
        
        if has_url:
            raw = config["url"]
            if isinstance(raw, str):
                ref.url = [raw]
            elif isinstance(raw, list) and all(isinstance(u, str) for u in raw):
                ref.url = raw
            else:
                print(f"ERROR: Package '{name}' url must be a string or list of strings.")
                exit(1)
        
        if has_git:
            ref.git = self._parse_git(config["git"], name)
        
        # B5: resolve
        if "resolve" in config:
            ref.resolve = config["resolve"]
        
        # B6: mode
        ref.mode = config.get("mode", "default")
        
        return ref
    
    # ═══════════════════════════════════════════
    # 分支 C: 其他类型 → 报错
    # ═══════════════════════════════════════════
    print(f"ERROR: Invalid package value for '{name}': type {type(value).__name__}."
          f" Expected string or object.")
    exit(1)
```

### 1.5 _parse_git() — Git 配置解析

```python
@staticmethod
def _parse_git(git_val, name: str) -> GitRef:
    if isinstance(git_val, str):
        return GitRef(url=git_val)
    
    if isinstance(git_val, dict):
        url = git_val.get("url")
        if not url:
            print(f"ERROR: Package '{name}' git config missing required 'url' field.")
            exit(1)
        return GitRef(
            url=url,
            tag=git_val.get("tag"),
            branch=git_val.get("branch"),
            hash=git_val.get("hash"),
        )
    
    print(f"ERROR: Package '{name}' git config must be a URL string or"
          f" an object with 'url' field. Got: {type(git_val).__name__}")
    exit(1)
```

### 1.6 缓存加载

```python
def _load_cache(self):
    if not os.path.exists(self.cache_path):
        return
    try:
        self.cache = Utils.loadJson(self.cache_path)
    except Exception:
        self.cache = {}

def save_cache(self):
    data = {
        "version": 1,
        "last_update": datetime.now().isoformat(),
        "resolved": {}
    }
    for ref in self.all_packages():
        if ref.real_package and ref.real_package.success:
            key = f"{ref.real_package.publisher}/{ref.real_package.name}"
            data["resolved"][key] = {
                "ref_hash": self._compute_ref_hash(ref),
                "publisher": ref.real_package.publisher,
                "name": ref.real_package.name,
                "version": ref.real_package.version,
                "path": ref.real_package.path,
            }
    os.makedirs(os.path.dirname(self.cache_path), exist_ok=True)
    with open(self.cache_path, "w") as f:
        json.dump(data, f, indent=2)

def get_cached(self, ref: RefPackage) -> LibPackage | None:
    key = f"{ref.publisher}/{ref.name}"
    entry = self.cache.get("resolved", {}).get(key)
    if not entry:
        return None
    if entry.get("ref_hash") != self._compute_ref_hash(ref):
        return None
    path = entry.get("path")
    if not path or not os.path.exists(path):
        return None
    return LibPackage(path)

@staticmethod
def _compute_ref_hash(ref: RefPackage) -> str:
    raw = json.dumps({
        "n": ref.name, "v": ref.version, "p": ref.publisher,
        "o": ref.origin, "path": ref.path, "url": ref.url,
        "g": ref.git.url if ref.git else None, "r": ref.resolve,
    }, sort_keys=True)
    return hashlib.sha256(raw.encode()).hexdigest()[:16]
```

### 1.7 设计决策：为什么 origin 正好是三个值？

| 值 | 语义 | 为什么不合并或拆分 |
|----|------|-------------------|
| `"local"` | 只在项目本地找, 不去系统 | 强制本地管理, 对应旧 forceLocal=true。不允许从系统取 → 保证版本一致性 |
| `"system"` | 只在系统找, 不下载 | 集中管理的包(公司内部库)。不允许自动下载 → 安全/审计需求 |
| `"default"` | 就近原则, 自动补全 | 对应旧 forceLocal=false, 最灵活。允许自动下载 → 开发效率优先 |

**为什么不支持 "system-then-local" 或 "local-then-download" 等更多组合？**

因为每个额外组合都增加复杂度, 而这三个已经覆盖了所有当前和可预见的用例。如果将来需要更多组合, 可以用 `[local, system]` 列表扩展 origin 字段, 但目前保持简单。

### 1.8 向后兼容处理

`AppConfig` 类保留, 内部委托 AppData:

```python
class AppConfig:
    """@deprecated: Use AppData instead. Kept for backward compatibility."""
    
    def __init__(self, path: str):
        print("WARNING: AppConfig is deprecated. Use AppData instead.")
        self._data = AppData(path)
        self.path = self._data.path
        self.success = True
        self.json = self._data.json
        self.localLibStore = self._data.local_lib_store
        self.forceLocal = (self._data.global_origin == "local")
        
        # 转换为旧 AppPackage 列表
        self.packages: list[AppPackage] = []
        for ref in self._data.packages:
            if not ref.skip:
                pkg = AppPackage.from_ref_package(ref)
                self.packages.append(pkg)
```

---

## 2. RefPackage — 替代 AppPackage

### 2.1 当前 AppPackage 的 5 个设计缺陷

```python
# AppPackage.py (60行, 当前代码)
class AppPackage:
    def __init__(self, name, version, path="", urls="", forceLocal=False):
        self.name = name.strip()          # ✅ 合理
        self.version = version.strip()    # ✅ 合理
        self.path = path.strip()          # ❌ 默认 "" 不代表 "无路径"
        self.urls = urls                  # ❌ 默认 "" 但注解是 list[str], 类型不一致
        self.forceLocal = forceLocal      # ❌ 全局二值, 不能表达 "system only"
        self.skip = self.version == "x"   # ✅ 合理
        self.versionSpec = ...            # ✅ 合理
        self.libPackage = None            # ❌ 命名歧义: "找到的包"不是 "lib 的包"
```

### 2.2 RefPackage 完整定义

```python
from packaging.specifiers import SpecifierSet
from dataclasses import dataclass, field

@dataclass
class GitRef:
    url: str
    tag: str | None = None
    branch: str | None = None
    hash: str | None = None
    # 优先级: hash > tag > branch > 默认分支

@dataclass
class RefPackage:
    """用户对包的引用声明——描述'我想要什么包'。
    解析后 real_package 描述'我找到了什么包'。"""
    
    # === 必要字段 ===
    name: str = ""
    publisher: str = ""             # 默认 "" = 不限制, 任何 publisher 的同名包均可
    is_global: bool = True          # 全局包可被任意 publisher 的同名包匹配
    version: str = "*"              # 版本范围字符串
    version_range: SpecifierSet = field(default_factory=lambda: SpecifierSet(">=0"))
    
    # === 来源字段 (三选一或都不选) ===
    path: str | None = None         # 本地路径
    url: list[str] | None = None    # 下载 URL 列表
    git: GitRef | None = None       # Git 仓库引用
    
    # === 配置字段 ===
    origin: str = "default"         # local | system | default
    mode: str = "default"           # default | sources | static | dynamic
    resolve: dict | None = None     # 文件解析规则
    
    # === 运行时字段 ===
    real_package: LibPackage | None = None
    skip: bool = False
    _is_external: bool = False
```

### 2.3 AppPackage 兼容层

```python
# 在 AppPackage.py 中添加
class AppPackage:
    """@deprecated: Use RefPackage instead."""
    
    @classmethod
    def from_ref_package(cls, ref: RefPackage) -> "AppPackage":
        pkg = cls.__new__(cls)
        pkg.name = ref.name
        pkg.version = ref.version
        pkg.path = ref.path or ""
        pkg.urls = ref.url or []
        pkg.forceLocal = (ref.origin == "local")
        pkg.skip = ref.skip
        pkg.versionSpec = ref.version_range
        pkg.libPackage = ref.real_package
        return pkg
```

---

## 3. origin 字段：三态替代二值 bool

### 3.1 在 PackageResolver 中的完整行为

```python
class PackageResolver:
    def resolve_one(self, ref: RefPackage):
        
        # ====== Phase 1: path 优先 (所有 origin 都一样) ======
        if ref.path:
            target = self._resolve_path(ref)
            if target is None:
                print(f"ERROR: Package '{ref.name}' specifies path '{ref.path}'"
                      f" but directory does not exist.")
                exit(1)
            
            lib = LibPackage(target)
            if not lib.success:
                print(f"ERROR: Failed to load package '{ref.name}' from path '{target}'."
                      f" Check that package.json exists and is valid.")
                exit(1)
            
            if not lib.isMatch(ref):
                print(f"ERROR: Package at '{target}' does not match"
                      f" the requested package '{ref.name}' (version {ref.version}).")
                exit(1)
            
            ref.real_package = lib
            return
        
        # ====== Phase 2: origin 分支 ======
        
        if ref.origin == "local":
            # 只查项目本地 .lib/
            lib = self._find_in_project_libs(ref)
            if lib is None:
                print(f"ERROR: Package '{ref.name}' not found in project local"
                      f" library ({self.env.appLibStore})."
                      f" Origin is 'local' — will not search system or download.")
                exit(1)
            ref.real_package = lib
            return
        
        elif ref.origin == "system":
            # 只查系统 DB
            lib = self._find_in_env_libs(ref)
            if lib is None:
                print(f"ERROR: Package '{ref.name}' version '{ref.version}'"
                      f" not found in system package index."
                      f" Run 'updateDb.py' to refresh the index,"
                      f" or check that the package exists in system lib stores.")
                exit(1)
            ref.real_package = lib
            return
        
        else:  # "default"
            # 先本地, 再系统
            lib = self._find_in_project_libs(ref)
            if lib is None:
                lib = self._find_in_env_libs(ref)
            
            if lib is not None:
                ref.real_package = lib
                return
            
            # 找不到 → 尝试下载
            if ref.url is not None:
                self._download_url(ref)
            elif ref.git is not None:
                self._download_git(ref)
            else:
                print(f"ERROR: Package '{ref.name}' version '{ref.version}'"
                      f" not found locally or in system, and no url/git specified"
                      f" for download.")
                exit(1)
```

---

## 4. url 下载完整流程

### 4.1 目标目录计算

```python
def _compute_target_dir(self, ref: RefPackage) -> str:
    if ref.path:
        return ref.path
    
    publisher = ref.publisher or "local"
    version = ref.version if ref.version not in ("*", "latest", "default", "") else "default"
    dir_name = f"{publisher}@{ref.name}@{version}"
    
    if ref.origin == "system":
        base = self.env.sysLibStore
    else:
        base = self.env.appLibStore
    
    return os.path.join(base, dir_name)
```

### 4.2 冲突检测

```python
def _check_conflict(self, ref: RefPackage, target: str) -> bool:
    """返回 True = 跳过下载 (已有有效包)"""
    if not os.path.exists(target):
        return False
    
    pkg_json = os.path.join(target, "package.json")
    
    # === 有 package.json ===
    if os.path.exists(pkg_json):
        data = Utils.loadJson(pkg_json)
        
        # name 校验
        actual_name = data.get("name", "")
        if actual_name != ref.name:
            print(f"ERROR: Existing package at '{target}' has name '{actual_name}',"
                  f" but expected '{ref.name}'. Remove the directory or fix the config.")
            exit(1)
        
        # publisher 校验
        actual_pub = data.get("publisher", "")
        if ref.publisher and actual_pub and ref.publisher != actual_pub:
            print(f"ERROR: Existing package at '{target}' has publisher '{actual_pub}',"
                  f" but expected '{ref.publisher}'.")
            exit(1)
        elif not ref.publisher and actual_pub:
            ref.publisher = actual_pub
            # 重命名目录以反映 publisher
            new_name = f"{ref.publisher}@{ref.name}@{ref.version or 'default'}"
            new_target = os.path.join(os.path.dirname(target), new_name)
            os.rename(target, new_target)
            target = new_target
        
        # version 校验
        actual_ver = data.get("version", "")
        if ref.version in ("*", "latest", "default", ""):
            if actual_ver:
                ref.version = actual_ver
                ref.version_range = Utils.parseVersionSpecifier(actual_ver)
                # 重命名目录
                new_name = f"{ref.publisher}@{ref.name}@{actual_ver}"
                new_target = os.path.join(os.path.dirname(target), new_name)
                if not os.path.exists(new_target):
                    os.rename(target, new_target)
                    target = new_target
        else:
            if not ref.version_range.contains(Version(actual_ver)):
                print(f"ERROR: Existing package at '{target}' has version '{actual_ver}',"
                      f" which does not match requested range '{ref.version}'."
                      f" Remove the directory or fix the version requirement.")
                exit(1)
        
        return True  # 已有有效包, 跳过下载
    
    # === 无 package.json 但有 resolve ===
    if ref.resolve is not None:
        return False  # 继续下载, 用 resolve 处理
    
    # === 既无 package.json 也无 resolve ===
    print(f"ERROR: Directory '{target}' exists but has no package.json,"
          f" and no resolve config is provided. Cannot use this directory.")
    exit(1)
```

### 4.3 下载执行

```python
def _download_url(self, ref: RefPackage):
    target = self._compute_target_dir(ref)
    
    # 冲突检测
    if self._check_conflict(ref, target):
        lib = LibPackage(target)
        if lib.success:
            ref.real_package = lib
            return
    
    # 下载
    downloader = UrlPackageDownload(ref, target, self.env)
    if not downloader.execute():
        print(f"ERROR: Failed to download package '{ref.name}' from URLs: {ref.url}")
        exit(1)
    
    # 验证
    ref.real_package = downloader.get_lib_package()
    if ref.real_package is None or not ref.real_package.success:
        print(f"ERROR: Downloaded package '{ref.name}' is invalid.")
        exit(1)
```

---

## 5. Git 下载

```python
class GitPackageDownload(BaseDownloader):
    def download(self) -> bool:
        url = self.ref.git.url
        result = subprocess.run(
            ["git", "clone", "--depth", "1", url, self.target_dir],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            print(f"ERROR: git clone failed for '{url}': {result.stderr.strip()}")
            return False
        
        ref = (self.ref.git.hash or
               f"tags/{self.ref.git.tag}" if self.ref.git.tag else
               self.ref.git.branch)
        
        if ref:
            result = subprocess.run(
                ["git", "-C", self.target_dir, "checkout", ref],
                capture_output=True, text=True
            )
            if result.returncode != 0:
                print(f"ERROR: git checkout '{ref}' failed: {result.stderr.strip()}")
                return False
        
        return True
```

---

## 6. resolve — 虚拟 LibPackage

```python
class LibPackage:
    @classmethod
    def _virtual_from_resolve(cls, path, name, publisher, version, resolve):
        lp = cls.__new__(cls)
        lp.name = name
        lp.publisher = publisher or "local"
        lp.version = version or "default"
        lp.path = os.path.normpath(path)
        lp.isGlobal = True
        lp.summary = f"[virtual package] {lp.publisher}/{lp.name}"
        lp.mode = resolve.get("mode", "sources") if resolve else "sources"
        lp.dependencies = []
        lp.success = True
        lp._virtual_resolve = resolve
        return lp
```

当 `PackageScanner` 遇到 `_virtual_resolve` 不为空的 LibPackage 时, 使用 resolve 数据替代默认扫描逻辑。

---

## 7. PackageResolver — 完整类

```python
class PackageResolver:
    def __init__(self, app_data: AppData, env: EnvConfig):
        self.app_data = app_data
        self.env = env
        self._project_libs: list[LibPackage] | None = None
    
    def resolve_all(self):
        for ref in self.app_data.packages:
            self._resolve_with_cache(ref)
        self._resolve_external_deps()
    
    def _resolve_with_cache(self, ref: RefPackage):
        cached = self.app_data.get_cached(ref)
        if cached is not None and os.path.exists(cached.path):
            ref.real_package = cached
            return
        self.resolve_one(ref)
    
    # resolve_one: 见 §3.1
    
    def _get_project_libs(self) -> list[LibPackage]:
        if self._project_libs is not None:
            return self._project_libs
        
        result = []
        lib_dir = self.env.appLibStore
        if os.path.exists(lib_dir):
            for entry in os.listdir(lib_dir):
                pkg_dir = os.path.join(lib_dir, entry)
                if not os.path.isdir(pkg_dir):
                    continue
                pkg_json = os.path.join(pkg_dir, "package.json")
                if not os.path.exists(pkg_json):
                    continue
                lib = LibPackage(pkg_dir)
                if lib.success:
                    result.append(lib)
        
        self._project_libs = result
        return result
    
    def _find_in_project_libs(self, ref: RefPackage) -> LibPackage | None:
        matching = []
        for lib in self._get_project_libs():
            if lib.isMatch(ref):
                matching.append(lib)
        matching.sort(key=lambda x: Version(x.version), reverse=True)
        return matching[0] if matching else None
    
    def _find_in_env_libs(self, ref: RefPackage) -> LibPackage | None:
        key = f"{ref.publisher}/{ref.name}"
        if key in self.env.libs:
            for lib in self.env.libs[key]:
                if ref.version_range.contains(Version(lib.version)):
                    return lib
        for k, libs in self.env.libs.items():
            if k.endswith(ref.name):
                for lib in libs:
                    if ref.version_range.contains(Version(lib.version)):
                        return lib
        return None
    
    def _resolve_external_deps(self):
        seen = set()
        changed = True
        max_iterations = 100
        iteration = 0
        
        while changed and iteration < max_iterations:
            changed = False
            iteration += 1
            current = self.app_data.all_packages()
            
            for ref in current:
                if not ref.real_package or not ref.real_package.success:
                    continue
                for dep in ref.real_package.dependencies:
                    dep_key = f"{dep.fullName}@{dep.version}"
                    if dep_key in seen:
                        continue
                    seen.add(dep_key)
                    
                    if self._is_dep_satisfied(dep, current):
                        continue
                    
                    ext = RefPackage()
                    ext.name = dep.fullName
                    ext.version = dep.version
                    ext.version_range = dep.versionSpec
                    ext.origin = ref.origin
                    ext._is_external = True
                    
                    self.resolve_one(ext)
                    self.app_data.external_packages.append(ext)
                    changed = True
        
        if iteration >= max_iterations:
            print("ERROR: Circular dependency detected or too many dependency levels.")
            exit(1)
```

---

## 8. IMakeCore 新旧对比

```python
# ═══ 当前 IMakeCore.py (26行) ═══
import sys
from scripts.data import *
from scripts.LocatePackage import *
from scripts.DownloadPackage import *
from scripts.MakeUtils import *

def loadPackages(app, env):
    for package in app.packages:
        if not (LocatePackages(package, env).success
             or DownloadPackage(package, env).success):
            print(f"Failed to locate or download package: {package.name}")
            exit(1)

if __name__ == '__main__':
    appPath = sys.argv[1]
    packType = sys.argv[2]
    env = EnvConfig(appPath, packType)
    app = AppConfig(appPath)
    loadPackages(app, env)
    MakeUtils.updatePackageForceLocal(app.packages, env)
    MakeUtils.checkPackageDependencies(app.packages)
    MakeUtils.createDumpJson(app.packages, env)
    MakeUtils.createIncludeFile(packType, app.packages, env)


# ═══ 目标 IMakeCore.py ═══
import sys
from scripts.data import *
from scripts.data.AppData import AppData
from scripts.PackageResolver import PackageResolver
from scripts.MakeUtils import *

if __name__ == '__main__':
    appPath = sys.argv[1]
    packType = sys.argv[2]
    
    env = EnvConfig(appPath, packType)
    app_data = AppData(appPath)
    
    resolver = PackageResolver(app_data, env)
    resolver.resolve_all()
    resolver._resolve_external_deps()
    
    all_pkgs = app_data.all_packages()
    
    MakeUtils.checkPackageDependencies(all_pkgs)
    MakeUtils.createDumpJson(all_pkgs, env)
    MakeUtils.createIncludeFile(packType, all_pkgs, env)
    
    app_data.save_cache()
```

---

## 9. 分阶段实施

| Wave | 文件 | 操作 |
|------|------|------|
| **W1** 数据模型 | `scripts/data/RefPackage.py` | NEW: RefPackage + GitRef |
|  | `scripts/data/AppData.py` | NEW: AppData + 缓存 |
|  | `scripts/data/AppPackage.py` | MODIFY: 添加 from_ref_package() |
|  | `scripts/data/AppConfig.py` | MODIFY: @deprecated, 委托 AppData |
|  | `scripts/data/LibPackage.py` | MODIFY: 添加 getDetail(), _virtual_from_resolve() |
|  | `scripts/data/__init__.py` | MODIFY: 导出新类 |
| **W2** 下载 | `scripts/util/download/BaseDownloader.py` | NEW |
|  | `scripts/util/download/UrlPackageDownload.py` | NEW |
|  | `scripts/util/download/GitPackageDownload.py` | NEW |
| **W3** 解析 | `scripts/PackageResolver.py` | NEW: 统一解析引擎 |
| **W4** 集成 | `scripts/IMakeCore.py` | MODIFY: 新流程 |
|  | `scripts/MakeUtils.py` | MODIFY: 适配 RefPackage |
| **W5** 清理 | 删除 AppConfig, AppPackage, LocatePackage, DownloadPackage | DELETE |
|  | 移除 forceLocal 所有引用 | MODIFY |

---

## 附录: 待定项

| # | 描述 | 建议 |
|---|------|------|
| 1 | path + url 同存: path 优先还是报错? | 互斥检查, 报错 (W1 实现) |
| 2 | 虚拟 LibPackage 写 DB? | 是, 添加 _virtual 列 (W1 实现) |
| 3 | 缓存自动失效 (DB mtime)? | 惰性, 手动清除 (W4 实现) |
| 4 | path=项目根目录时 generator 跳过? | 检查 real_package.path==project_path (W3 实现) |
| 5 | `from data import *` 改显式导入? | 可选, W5 清理 |
