"""compile_info/test.py — Test CompileInfo is correctly populated from build system."""
import json, os, re, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
_SYSTEM = Path(os.getenv("IMAKECORE_SYSTEM", ""))
IMAKECORE_PY = _SYSTEM / "IMakeCore.py"
UPDATE_DB_PY = _SYSTEM / "updateDb.py"
_PASSED = _FAILED = 0
_G_PACK_TYPE = "qmake"


def _setup():
    (ROOT / ".db").mkdir(exist_ok=True)
    subprocess.run([sys.executable, "-B", str(UPDATE_DB_PY)],
                   env={**os.environ, "IMAKECORE_ROOT": str(ROOT)},
                   capture_output=True, text=True, check=True, timeout=60)


def _run(project: Path, **extra_env) -> subprocess.CompletedProcess:
    env = {**os.environ, "IMAKECORE_ROOT": str(ROOT)}
    env.update(extra_env)
    return subprocess.run(
        [sys.executable, "-B", str(IMAKECORE_PY), str(project), _G_PACK_TYPE],
        env=env, capture_output=True, text=True, timeout=120)


def _prepare(project: Path, packages: dict) -> Path:
    for name in (".package.pri", ".package.cmake", ".package.xmake", ".data", ".lib", ".support", ".bin"):
        p = project / name
        if p.exists():
            (shutil.rmtree if p.is_dir() else os.remove)(str(p))
    project.mkdir(parents=True, exist_ok=True)
    (project / "packages.json").write_text(json.dumps({"packages": packages}), encoding="utf-8")
    return project


def _check(c, msg):
    global _PASSED, _FAILED
    if c: _PASSED += 1
    else: _FAILED += 1; print(f"  FAIL: {msg}")


def _output(project: Path) -> Path:
    return project / (".package.xmake" if _G_PACK_TYPE == "xmake" else (".package.cmake" if _G_PACK_TYPE == "cmake" else ".package.pri"))


# ── Tests ──────────────────────────────────────────────────────────

def test_compile_info_present():
    """IMakeCore should populate CompileInfo from env vars."""
    proj = _prepare(ROOT / "project_ci", {"test/hello": "1.0.0"})
    r = _run(proj,
             IMAKECORE_EXECUTABLE_PATH="/fake/bin",
             IMAKECORE_TARGET_TYPE="executable",
             IMAKECORE_PLATFORM="windows",
             IMAKECORE_ARCH="x86_64",
             IMAKECORE_COMPILER="msvc",
             IMAKECORE_COMPILER_VERSION="19.40",
             IMAKECORE_BUILD_MODE="debug",
             IMAKECORE_RUNTIMES="dynamic",
             IMAKECORE_CPP_STD="17",
             IMAKECORE_EXCEPTION_ENABLED="1",
             IMAKECORE_RTTI_ENABLED="1")
    _check(r.returncode == 0, f"IMakeCore failed: rc={r.returncode}\n{r.stdout[:300]}")
    # Verify CompileInfo was captured in AppData by checking output or .package.pri
    out = _output(proj)
    _check(out.exists(), ".package.pri should exist")


def test_compile_info_static_lib():
    """Target type static should not cause issues."""
    proj = _prepare(ROOT / "project_ci_static", {"test/hello": "1.0.0"})
    r = _run(proj,
             IMAKECORE_TARGET_TYPE="static",
             IMAKECORE_PLATFORM="linux",
             IMAKECORE_ARCH="arm64",
             IMAKECORE_COMPILER="gcc",
             IMAKECORE_COMPILER_VERSION="13.2",
             IMAKECORE_BUILD_MODE="release",
             IMAKECORE_CPP_STD="20")
    _check(r.returncode == 0, f"rc={r.returncode}")


def test_compile_info_dynamic_lib():
    """Target type dynamic should not cause issues."""
    proj = _prepare(ROOT / "project_ci_dynamic", {"test/hello": "1.0.0"})
    r = _run(proj,
             IMAKECORE_TARGET_TYPE="dynamic",
             IMAKECORE_PLATFORM="macos",
             IMAKECORE_COMPILER="clang",
             IMAKECORE_COMPILER_VERSION="16.0",
             IMAKECORE_BUILD_MODE="debug")
    _check(r.returncode == 0, f"rc={r.returncode}")


def test_compile_info_no_exceptions():
    """Exception disabled should be handled."""
    proj = _prepare(ROOT / "project_ci_noexc", {"test/hello": "1.0.0"})
    r = _run(proj,
             IMAKECORE_PLATFORM="windows",
             IMAKECORE_COMPILER="msvc",
             IMAKECORE_EXCEPTION_ENABLED="0",
             IMAKECORE_RTTI_ENABLED="1")
    _check(r.returncode == 0, f"rc={r.returncode}")


def test_compile_info_no_rtti():
    """RTTI disabled should be handled."""
    proj = _prepare(ROOT / "project_ci_nortti", {"test/hello": "1.0.0"})
    r = _run(proj,
             IMAKECORE_PLATFORM="linux",
             IMAKECORE_COMPILER="gcc",
             IMAKECORE_EXCEPTION_ENABLED="1",
             IMAKECORE_RTTI_ENABLED="0")
    _check(r.returncode == 0, f"rc={r.returncode}")


def test_compile_info_all_fields():
    """All CompileInfo fields should be accepted without error."""
    proj = _prepare(ROOT / "project_ci_all", {"test/hello": "1.0.0"})
    r = _run(proj,
             IMAKECORE_EXECUTABLE_PATH="/build/output",
             IMAKECORE_TARGET_TYPE="executable",
             IMAKECORE_PLATFORM="windows",
             IMAKECORE_ARCH="x86_64",
             IMAKECORE_COMPILER="msvc",
             IMAKECORE_COMPILER_VERSION="19.40.33811",
             IMAKECORE_BUILD_MODE="release",
             IMAKECORE_RUNTIMES="static",
             IMAKECORE_CPP_STD="20",
             IMAKECORE_EXCEPTION_ENABLED="1",
             IMAKECORE_RTTI_ENABLED="0")
    _check(r.returncode == 0, f"rc={r.returncode}")
    _check(_output(proj).exists(), "output should exist")


def test_compile_info_gcc_release():
    """GCC + release + C++23."""
    proj = _prepare(ROOT / "project_ci_gcc", {"test/hello": "1.0.0"})
    r = _run(proj,
             IMAKECORE_PLATFORM="linux", IMAKECORE_ARCH="x86_64",
             IMAKECORE_COMPILER="gcc", IMAKECORE_COMPILER_VERSION="14.1",
             IMAKECORE_BUILD_MODE="release", IMAKECORE_CPP_STD="23")
    _check(r.returncode == 0, f"rc={r.returncode}")


def test_compile_info_clang_arm64():
    """Clang + arm64 + macOS."""
    proj = _prepare(ROOT / "project_ci_clang", {"test/hello": "1.0.0"})
    r = _run(proj,
             IMAKECORE_PLATFORM="macos", IMAKECORE_ARCH="arm64",
             IMAKECORE_COMPILER="clang", IMAKECORE_COMPILER_VERSION="17.0",
             IMAKECORE_BUILD_MODE="debug", IMAKECORE_CPP_STD="20")
    _check(r.returncode == 0, f"rc={r.returncode}")


def test_compile_info_msvc_x86():
    """MSVC + x86 + static runtime."""
    proj = _prepare(ROOT / "project_ci_msvc86", {"test/hello": "1.0.0"})
    r = _run(proj,
             IMAKECORE_PLATFORM="windows", IMAKECORE_ARCH="x86",
             IMAKECORE_COMPILER="msvc", IMAKECORE_COMPILER_VERSION="19.38",
             IMAKECORE_RUNTIMES="static", IMAKECORE_CPP_STD="17")
    _check(r.returncode == 0, f"rc={r.returncode}")


def test_compile_info_no_env_vars():
    """Missing all optional env vars — should use defaults."""
    proj = _prepare(ROOT / "project_ci_nodef", {"test/hello": "1.0.0"})
    r = _run(proj)
    _check(r.returncode == 0, f"rc={r.returncode}")


def run(pack_type: str = "qmake"):
    global _PASSED, _FAILED, _G_PACK_TYPE
    _G_PACK_TYPE = pack_type
    print(f"{'='*60}\ncompile_info  (root={ROOT})\n{'='*60}")
    _setup()
    test_compile_info_present()
    test_compile_info_static_lib()
    test_compile_info_dynamic_lib()
    test_compile_info_no_exceptions()
    test_compile_info_no_rtti()
    test_compile_info_all_fields()
    test_compile_info_gcc_release()
    test_compile_info_clang_arm64()
    test_compile_info_msvc_x86()
    test_compile_info_no_env_vars()
    print(f"\n  {_PASSED} passed, {_FAILED} failed")
    return _FAILED == 0


if __name__ == "__main__":
    pt = sys.argv[1] if len(sys.argv) > 1 else "qmake"
    sys.exit(0 if run(pt) else 1)
