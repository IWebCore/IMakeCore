# IMAKECORE2

C/C++ package manager — npm/pip-style dependency resolution for qmake and CMake projects. Python orchestration engine, C++ library hosting.

## STRUCTURE

```
IMakeCore2/
├── .system/                       # Python package engine
│   ├── IMakeCore.py               # CLI entry: load → locate → download → generate
│   ├── IMakeCore_loadFiles.py     # C/C++ file scanner (arg: dir suffix...)
│   ├── .IMakeCore.cmake           # CMake macros: ICmakeCoreInit(), autoLoadPackage()
│   ├── .IMakeCore.prf             # qmake macros: IQMakeCoreInit(), autoLoadPackage()
│   └── scripts/
│       ├── data/                  # Domain models
│       │   ├── AppConfig.py       # Reads project's packages.json
│       │   ├── AppPackage.py      # User-facing package spec (name, version, path, forceLocal)
│       │   ├── LibPackage.py      # Library manifest (package.json inside .lib/ dirs)
│       │   └── EnvConfig.py       # Path resolution, server list, lib index from all stores
│       ├── Utils.py               # JSON loader (BOM-safe), version specifier parser
│       ├── MakeUtils.py           # Generates .package.pri / .package.cmake include chains
│       ├── LocatePackage.py       # Match AppPackage against local .lib/ inventory
│       └── DownloadPackage.py     # Fetch .zip from servers, validate, unpack
├── .lib/                          # Global package store (publisher@name@version/)
├── .data/
│   ├── config.json                # servers[], libstores[], globalLibStore, user
│   └── packages.json              # Template copied to new projects
├── .cache/                        # Transient download cache
├── .programs/{linux,windows}/     # Platform binaries (ipc.exe, Qt6Core.dll)
├── windows_install.bat            # Sets IMAKECORE_ROOT, IQMakeCore, ICMakeCore env vars
└── linux_install.sh               # /etc/profile.d + /etc/environment + symlinks
```

## ENTRY POINTS

### For end-users (C++ projects):
1. Add `packages.json` with `{"packages": {"nlohmann.json": "*", ...}}`
2. CMake: `include($ENV{ICMakeCore})` then `ICmakeCoreInit(target1 target2)`
3. qmake: `include($$ICMakeCore)` then `IQMakeCoreInit()`

### Internal flow:
```
packages.json → AppConfig → AppPackage[] → LocatePackage (local match)
                                            ↓ miss
                                           DownloadPackage (HTTP → zip → unpack)
                                            ↓
                                           MakeUtils → .package.{pri,cmake}
                                            ↓
                                           CMake/qmake `include()` → autoLoadPackage()
```

## WHERE TO LOOK

| Task | Location | Notes |
|------|----------|-------|
| Add package metadata fields | `scripts/data/LibPackage.py` → `loadPackage()` | Both app and lib share package.json schema |
| Change download behavior | `scripts/DownloadPackage.py` | `downloadByServer()` builds URL, `downloadByUrl()` handles direct links |
| Modify generated build file format | `scripts/MakeUtils.py` → `qmakePostProcess()` / `cmakePostProcess()` | Output is `.package.pri` / `.package.cmake` |
| Add new build system | `EnvConfig.py` (makeType), `MakeUtils.py` (createIncludeFile) | Currently: `qmake`, `cmake` |
| Change version matching logic | `scripts/Utils.py` → `parseVersionSpecifier()` | Supports `==x.y`, `>=x.y`, `*`, `x` (skip) |
| Add server protocol | `scripts/DownloadPackage.py` | Currently: `GET /package/download?name=&version=` |
| Change environment variable names | Both install scripts + `EnvConfig.py` | `IMAKECORE_ROOT` is the root; `ICMakeCore`/`IQMakeCore` point to integration files |

## CONVENTIONS

### Package naming: `publisher@name@version`
- Lib store directories: `yuekeyuan@ICore@1.1.0/`
- Include files: `yuekeyuan@ICore@1.1.0.pri` or `.package.pri`
- Download URLs encode name with `@` instead of `/`

### package.json schema (both app-level and lib-level)
```json
{
  "name": "ICore",
  "version": "1.1.0",
  "publisher": "yuekeyuan",
  "isGlobal": true,
  "autoScan": true,
  "summary": "...",
  "dependencies": { "nlohmann.json": "*" },
  "links": ["https://github.com/..."],
  "changelog": ["..."]
}
```
- `isGlobal: false` + empty publisher → **fatal error** (must have publisher for local packages)
- `autoScan: true` → engine auto-discovers .h/.cpp/.ui/.rcc via Python scanner
- `autoScan: false` → requires explicit `.pri`/`.cmake` include file

### Version specifiers
- `"*"` or `"latest"` → any version (resolves to latest available)
- `"x"` → **skip this package** (removes from dependency list)
- `"1.2.3"` → exact match
- `">=1.0,<2.0"` → SemVer range (packaging.specifiers)

### Build file generation is idempotent
`MakeUtils.createIncludeFile()` compares generated content with existing file — exits 0 if identical, avoiding unnecessary CMake/qmake reconfiguration.

## ANTI-PATTERNS

- **NEVER** edit `.package.pri` / `.package.cmake` — they are `# SYSTEM AUTO GENERATED DO NOT EDIT!!!`
- **NEVER** edit the auto-scan `.pri`/`.cmake` files in `.lib/` store
- **NEVER** set `isGlobal: false` without a `publisher` field
- **NEVER** use `BOM` in JSON files (engine strips it, but don't create them)
- **NEVER** put spaces in package names containing `/` — use `publisher/name` or bare `name`

## COMMANDS

```bash
# Install (Windows, as admin)
.\windows_install.bat

# Install (Linux, as root)
sudo bash linux_install.sh

# Run package resolution manually (testing)
python -B .system/IMakeCore.py <project-dir> cmake|qmake

# Scan C/C++ files in a directory
python -B .system/IMakeCore_loadFiles.py <dir> .h .hpp .cpp .c
```

## FULL FLOW

See [`.system/FLOW.md`](.system/FLOW.md) for the complete pipeline from `ipc init` → environment setup → package resolution → auto-scan → qmake/CMake target assembly.

## NOTES

- `EnvConfig` constructs path map from `IMAKECORE_ROOT` env var — **must be set** before any operation
- Server discovery: tries each `config.json → servers[]` URL in order, first success wins
- Package match uses publisher-scoped lookups when name contains `/`, otherwise matches any global package
- `forceLocal: true` copies package from its location into the project's `.lib/` store
- `LibPackage.__init__` is defined twice in the source (second overwrites first) — intentional or Python quirk
- Downloaded packages are cached as timestamped `.zip` files in `.cache/`, deleted after unpack