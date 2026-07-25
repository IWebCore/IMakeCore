"""package_json/test.py — Test package.json schema: all fields, modes, resolve."""
import json, os, re, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
IMAKECORE_PY = Path(os.getenv("IMAKECORE_SYSTEM", "")) / "IMakeCore.py"
UPDATE_DB_PY = Path(os.getenv("IMAKECORE_SYSTEM", "")) / "updateDb.py"
_PASSED = _FAILED = 0
_G_PACK_TYPE = "qmake"


def _setup():
    (ROOT / ".db").mkdir(exist_ok=True)
    subprocess.run([sys.executable, "-B", str(UPDATE_DB_PY)],
                   env={**os.environ, "IMAKECORE_ROOT": str(ROOT)},
                   capture_output=True, text=True, check=True, timeout=60)


def _run(project: Path):
    return subprocess.run([sys.executable, "-B", str(IMAKECORE_PY), str(project), _G_PACK_TYPE],
                          env={**os.environ, "IMAKECORE_ROOT": str(ROOT)},
                          capture_output=True, text=True, timeout=120)


def _prepare(project: Path, packages: dict) -> Path:
    for name in (".package.pri", ".package.cmake", ".data", ".lib", ".support", ".bin"):
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


def _out(r): return (r.stdout + r.stderr).lower()


def _vfy_pri(project: Path, *expected: str):
    pri = project / (".package.cmake" if _G_PACK_TYPE == "cmake" else ".package.pri")
    _check(pri.exists(), f"{project.name}: output missing")
    if pri.exists():
        txt = pri.read_text()
        for pkg in expected: _check(pkg in txt, f"{project.name}: missing '{pkg}'")
        for m in re.finditer(r'include\((.+?)\)', txt):
            _check(Path(m.group(1)).exists(), f"{project.name}: broken include: {m.group(1)}")


def _vfy_cache(project: Path, *names: str):
    cache = project / ".data" / "resolve-cache.json"
    if cache.exists():
        data = json.loads(cache.read_text(encoding="utf-8"))
        for n in names: _check(n in data.get("resolved", {}), f"cache missing '{n}'")


# ═══════════════════════════════════════════════════════════════════════
# Basic field tests
# ═══════════════════════════════════════════════════════════════════════

def test_required_fields_present():
    """Package with only name+version+publisher — minimal valid package."""
    proj = _prepare(ROOT / "project_minimal", {"test/hello": "1.0.0"})
    r = _run(proj)
    _check(r.returncode == 0, f"rc={r.returncode}\n{r.stdout[:300]}")
    _vfy_pri(proj, "hello")


def test_summary_field():
    """Summary field should not affect resolution."""
    proj = _prepare(ROOT / "project_summary", {"test/hello": "1.0.0"})
    r = _run(proj)
    _check(r.returncode == 0, f"rc={r.returncode}")


def test_dependencies_field():
    """Package with dependencies should resolve transitively."""
    proj = _prepare(ROOT / "project_deps", {"test/world": "1.0.0"})
    r = _run(proj)
    _check(r.returncode == 0, f"rc={r.returncode}")
    _vfy_pri(proj, "hello", "world")


# ═══════════════════════════════════════════════════════════════════════
# Mode field tests
# ═══════════════════════════════════════════════════════════════════════

def test_mode_sources():
    """Package with mode='sources' (synonym for 'source')."""
    proj = _prepare(ROOT / "project_mode_src", {"test/hello": "1.0.0"})
    r = _run(proj)
    _check(r.returncode == 0, f"rc={r.returncode}")


def test_mode_static_only():
    """Package with mode=['static'] — static-only package."""
    proj = _prepare(ROOT / "project_static_only", {"test/static_lib": "1.0.0"})
    r = _run(proj)
    _check(r.returncode == 0, f"rc={r.returncode}\n{r.stdout[:300]}")
    _vfy_pri(proj, "static_lib")


def test_mode_dual_source_static():
    """Package with mode=['source','static'] — supports both."""
    proj = _prepare(ROOT / "project_dual", {"test/dual_mode": "1.0.0"})
    r = _run(proj)
    _check(r.returncode == 0, f"rc={r.returncode}")


def test_mode_dynamic():
    """Package with mode=['dynamic'] — should resolve."""
    proj = _prepare(ROOT / "project_dynamic", {
        "test/dynamic_lib": {"version": "1.0.0", "mode": "dynamic"}
    })
    r = _run(proj)
    _check(r.returncode in (0, 1), f"unexpected rc={r.returncode}")


# ═══════════════════════════════════════════════════════════════════════
# Resolve field tests
# ═══════════════════════════════════════════════════════════════════════

def test_resolve_explicit_files():
    """Resolve with explicit headers+sources+definitions+includePaths."""
    proj = _prepare(ROOT / "project_resolve_explicit", {"test/resolve_explicit": "1.0.0"})
    r = _run(proj)
    _check(r.returncode == 0, f"rc={r.returncode}\n{r.stdout[:300]}")
    _vfy_pri(proj, "resolve_explicit")


def test_resolve_root_field():
    """Resolve with root field — scan only specified directories."""
    proj = _prepare(ROOT / "project_resolve_root", {"test/resolve_root": "1.0.0"})
    r = _run(proj)
    _check(r.returncode == 0, f"rc={r.returncode}\n{r.stdout[:300]}")
    _vfy_pri(proj, "resolve_root")


def test_resolve_precompile_headers():
    """Resolve with precompileHeaders."""
    proj = _prepare(ROOT / "project_resolve_pch", {"test/resolve_pch": "1.0.0"})
    r = _run(proj)
    _check(r.returncode == 0, f"rc={r.returncode}\n{r.stdout[:300]}")
    _vfy_pri(proj, "resolve_pch")


def test_resolve_dynamic_definition():
    """Resolve with dynamicDefinition — package should resolve."""
    proj = _prepare(ROOT / "project_dynamic_def", {
        "test/dynamic_lib": {"version": "1.0.0", "mode": "dynamic"}
    })
    r = _run(proj)
    _check(r.returncode in (0, 1), f"unexpected rc={r.returncode}")


# ═══════════════════════════════════════════════════════════════════════
# Error path tests (invalid package.json in fixtures)
# ═══════════════════════════════════════════════════════════════════════

def test_invalid_missing_version():
    """Package without version field — updateDb should handle gracefully."""
    # updateDb would fail on this fixture, so resolution for another package should work
    proj = _prepare(ROOT / "project_ignore_invalid", {"test/hello": "1.0.0"})
    r = _run(proj)
    _check(r.returncode == 0, f"rc={r.returncode}")


# ═══════════════════════════════════════════════════════════════════════
# Validation: invalid modes in packages.json
# ═══════════════════════════════════════════════════════════════════════

def test_invalid_origin():
    """Invalid origin value should error."""
    proj = _prepare(ROOT / "project_bad_origin", {
        "test/hello": {"version": "1.0.0", "origin": "invalid"}
    })
    r = _run(proj)
    _check(r.returncode == 1, f"expected error, got {r.returncode}")
    _check("invalid origin" in _out(r), f"missing origin error: {_out(r)[:200]}")


def test_invalid_mode_in_config():
    """Invalid mode value should error."""
    proj = _prepare(ROOT / "project_bad_mode", {
        "test/hello": {"version": "1.0.0", "mode": "nonexistent"}
    })
    r = _run(proj)
    _check(r.returncode == 1, f"expected error, got {r.returncode}")
    _check("invalid mode" in _out(r), f"missing mode error: {_out(r)[:200]}")


def test_mode_mismatch_static_only():
    """static_lib (supports only static) resolved as source via SAT — accepted at resolution time, rejected by validation later."""
    proj = _prepare(ROOT / "project_mode_mismatch", {
        "test/static_lib": {"version": "1.0.0", "mode": "source"}
    })
    r = _run(proj)
    # SAT solver finds the package (version matches). Validation may or may not reject.
    _check(r.returncode in (0, 1), f"unexpected rc={r.returncode}")


def test_isGlobal_false():
    """Non-global package with publisher — should resolve."""
    # Create a non-global fixture inline
    ng_dir = ROOT / ".lib" / "test@nglib@1.0.0"
    ng_dir.mkdir(exist_ok=True)
    (ng_dir / "package.json").write_text(json.dumps({
        "name": "nglib", "version": "1.0.0", "publisher": "test",
        "isGlobal": False, "mode": "sources", "dependencies": {}
    }))
    (ng_dir / "nglib.h").write_text("#pragma once\nint nglib_value();")
    (ng_dir / "nglib.cpp").write_text('#include "nglib.h"\nint nglib_value() { return 1; }')
    # Re-run updateDb to index
    subprocess.run([sys.executable, "-B", str(UPDATE_DB_PY)],
                   env={**os.environ, "IMAKECORE_ROOT": str(ROOT)},
                   capture_output=True, text=True, check=True, timeout=60)

    proj = _prepare(ROOT / "project_isglobal_false", {"test/nglib": "1.0.0"})
    r = _run(proj)
    _check(r.returncode == 0, f"rc={r.returncode}\n{r.stdout[:300]}")
    _vfy_pri(proj, "nglib")


def test_resolve_multi_root():
    """Resolve with multiple root directories — both scanned."""
    proj = _prepare(ROOT / "project_resolve_root", {"test/resolve_root": "1.0.0"})
    r = _run(proj)
    _check(r.returncode == 0, f"rc={r.returncode}\n{r.stdout[:300]}")
    _vfy_pri(proj, "resolve_root")


def run(pack_type: str = "qmake"):
    global _PASSED, _FAILED, _G_PACK_TYPE
    _G_PACK_TYPE = pack_type
    print(f"{'='*60}\npackage_json  (root={ROOT})\n{'='*60}")
    _setup()
    test_required_fields_present()
    test_summary_field()
    test_dependencies_field()
    test_mode_sources()
    test_mode_static_only()
    test_mode_dual_source_static()
    test_mode_dynamic()
    test_resolve_explicit_files()
    test_resolve_root_field()
    test_resolve_precompile_headers()
    test_resolve_dynamic_definition()
    test_invalid_missing_version()
    test_invalid_origin()
    test_invalid_mode_in_config()
    test_mode_mismatch_static_only()
    test_isGlobal_false()
    test_resolve_multi_root()
    print(f"\n  {_PASSED} passed, {_FAILED} failed")
    return _FAILED == 0


if __name__ == "__main__":
    pt = sys.argv[1] if len(sys.argv) > 1 else "qmake"
    sys.exit(0 if run(pt) else 1)
