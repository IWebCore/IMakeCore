# IMakeCore

C/C++ package manager — npm/pip-style dependency resolution for qmake, CMake, and xmake projects. A Python orchestration engine resolves, downloads, and wires up packages; C++ libraries are hosted in a global store and exposed to your build system.

## Install

Windows (as admin):

```bat
.\windows_install.bat
```

Linux (as root):

```bash
sudo bash linux_install.sh
```

Both scripts register three environment variables pointing at the integration files:

| Variable    | Build system | Integration file            |
|-------------|--------------|-----------------------------|
| `IQMakeCore` | qmake        | `.system/.IMakeCore.prf`     |
| `ICMakeCore` | CMake        | `.system/.IMakeCore.cmake`   |
| `IXMakeCore` | xmake        | `.system/.IMakeCore.xmake`   |

The scripts also register `IMAKECORE_ROOT`, which must be set before any resolution runs.

## Usage

Add a `packages.json` to your project root declaring the packages you depend on:

```json
{ "packages": { "nlohmann.json": "*" } }
```

Then wire IMakeCore into your build system.

### qmake

In your `.pro` file:

```qmake
include($$(IQMakeCore))
IQMakeCoreInit()
```

### CMake

In your `CMakeLists.txt`:

```cmake
include($ENV{ICMakeCore})
ICmakeCoreInit(target)
```

### xmake

In your `xmake.lua`:

```lua
local imake = os.getenv("IXMakeCore")
if imake then includes(imake) end
imakecore_init(os.scriptdir())
```

## Manual resolution

Resolution normally runs automatically through the build system. To run it by hand (e.g. for testing):

```bash
python -B .system/IMakeCore.py <project-dir> qmake|cmake|xmake
```
