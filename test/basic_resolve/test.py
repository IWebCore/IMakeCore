"""
basic_resolve/test.py — Self-contained functional test.

This directory IS the IMAKECORE_ROOT.
"""
import json, os, re, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
IMAKECORE_PY = ROOT / ".system" / "IMakeCore.py"
UPDATE_DB_PY = ROOT / ".system" / "scripts" / "updateDb.py"
_PASSED = _FAILED = 0


# ── Environment ────────────────────────────────────────────────────────
def _setup():
    (ROOT / ".db").mkdir(exist_ok=True)
    subprocess.run([sys.executable, "-B", str(UPDATE_DB_PY)],
                   env={**os.environ, "IMAKECORE_ROOT": str(ROOT)},
                   capture_output=True, text=True, check=True, timeout=60)


def _run(project: Path):
    return subprocess.run([sys.executable, "-B", str(IMAKECORE_PY), str(project), "qmake"],
                          env={**os.environ, "IMAKECORE_ROOT": str(ROOT)},
                          capture_output=True, text=True, timeout=120)


def _prepare(project: Path, packages: dict) -> Path:
    """Clean old artefacts (BEFORE each run), write fresh packages.json."""
    for name in (".package.pri", ".package.cmake", ".data", ".lib", ".support", ".bin"):
        p = project / name
        if p.exists():
            (shutil.rmtree if p.is_dir() else os.remove)(str(p))
    project.mkdir(parents=True, exist_ok=True)
    (project / "packages.json").write_text(json.dumps({"packages": packages}), encoding="utf-8")
    return project


# ── Checks ─────────────────────────────────────────────────────────────
def _check(c, msg):
    global _PASSED, _FAILED
    if c: _PASSED += 1
    else: _FAILED += 1; print(f"  FAIL: {msg}")


# ── Verification helpers ───────────────────────────────────────────────
def _vfy_pri_exists(project: Path, *expected_packages: str):
    """Verify .package.pri exists and includes each expected package."""
    pri = project / ".package.pri"
    _check(pri.exists(), f"{project.name}: .package.pri not generated")
    if not pri.exists():
        return ""
    txt = pri.read_text()
    for pkg in expected_packages:
        _check(pkg in txt, f"{project.name}: .package.pri missing package '{pkg}'")
    return txt


def _vfy_pri_absent(project: Path, *forbidden: str):
    """Verify .package.pri does NOT include forbidden packages."""
    pri = project / ".package.pri"
    if not pri.exists():
        return
    txt = pri.read_text()
    for pkg in forbidden:
        _check(pkg not in txt, f"{project.name}: .package.pri leaked forbidden '{pkg}'")


def _vfy_pri_includes_exist(project: Path):
    """Every include() path in .package.pri must reference a real file."""
    pri = project / ".package.pri"
    if not pri.exists():
        return
    for m in re.finditer(r'include\((.+?)\)', pri.read_text()):
        path = Path(m.group(1))
        _check(path.exists(), f"{project.name}: include target missing: {path}")


def _vfy_lib_pri_exists(project: Path, *pkg_names: str):
    """Verify .lib/ contains .pri files for each resolved package."""
    lib = project / ".lib"
    _check(lib.exists(), f"{project.name}: .lib/ not created")
    if not lib.exists():
        return
    for name in pkg_names:
        found = any(name in p.name for p in lib.glob("*.pri"))
        _check(found, f"{project.name}: .lib/ missing .pri for '{name}'")


def _vfy_resolve_cache(project: Path, *pkg_names: str):
    """Verify .data/resolve-cache.json contains entries for resolved packages."""
    cache = project / ".data" / "resolve-cache.json"
    _check(cache.exists(), f"{project.name}: resolve-cache.json not generated")
    if not cache.exists():
        return
    data = json.loads(cache.read_text(encoding="utf-8"))
    resolved = data.get("resolved", {})
    for name in pkg_names:
        _check(name in resolved, f"{project.name}: resolve-cache missing '{name}'")


def _vfy_pri_order(project: Path, *ordered: str):
    """Verify that includes appear in the correct order (deps before dependents)."""
    pri = project / ".package.pri"
    if not pri.exists():
        return
    txt = pri.read_text()
    positions = {}
    for name in ordered:
        idx = txt.find(name)
        _check(idx >= 0, f"{project.name}: '{name}' not found for order check")
        positions[name] = idx
    for a, b in zip(ordered, ordered[1:]):
        _check(positions.get(a, -1) < positions.get(b, -1),
               f"{project.name}: expected '{a}' before '{b}'")


# ── Test cases ─────────────────────────────────────────────────────────

def test_single_package_no_deps():
    """hello@1.0.0 — single header-only package."""
    proj = _prepare(ROOT / "project_single", {"test/hello": "1.0.0"})
    r = _run(proj)
    _check(r.returncode == 0, f"rc={r.returncode}")

    _vfy_pri_exists(proj, "hello")
    _vfy_pri_includes_exist(proj)
    _vfy_lib_pri_exists(proj, "hello")
    _vfy_resolve_cache(proj, "test/hello")


def test_single_source_package():
    """hello@2.0.0 — source package with .cpp."""
    proj = _prepare(ROOT / "project_source", {"test/hello": "2.0.0"})
    r = _run(proj)
    _check(r.returncode == 0, f"rc={r.returncode}")

    _vfy_pri_exists(proj, "hello")
    _vfy_pri_includes_exist(proj)
    _vfy_lib_pri_exists(proj, "hello")
    _vfy_resolve_cache(proj, "test/hello")


def test_transitive_dependency():
    """world@1.0.0 → hello — both must resolve, deps first."""
    proj = _prepare(ROOT / "project_transitive", {"test/world": "1.0.0"})
    r = _run(proj)
    _check(r.returncode == 0, f"rc={r.returncode}")

    _vfy_pri_exists(proj, "hello", "world")
    _vfy_pri_includes_exist(proj)
    _vfy_lib_pri_exists(proj, "hello", "world")
    _vfy_resolve_cache(proj, "test/hello", "test/world")


def test_version_selection_latest():
    """>=2.0 → must pick 2.0.0, not 1.0.0."""
    proj = _prepare(ROOT / "project_version", {"test/hello": ">=2.0"})
    r = _run(proj)
    _check(r.returncode == 0, f"rc={r.returncode}")

    pri = proj / ".package.pri"
    txt = pri.read_text() if pri.exists() else ""
    _check("2.0.0" in txt, "version 2.0.0 not selected")
    _check("1.0.0" not in txt, "version 1.0.0 leaked into output")
    _vfy_pri_includes_exist(proj)
    _vfy_resolve_cache(proj, "test/hello")


def test_version_skip():
    """Version 'x' → package must be excluded from output."""
    proj = _prepare(ROOT / "project_skip", {"test/hello": "x"})
    r = _run(proj)
    _check(r.returncode == 0, f"rc={r.returncode}")

    _vfy_pri_absent(proj, "hello")
    # .lib/ should not have hello .pri
    lib = proj / ".lib"
    if lib.exists():
        _check(not any("hello" in p.name for p in lib.glob("*.pri")),
               "hello .pri leaked into .lib/")


# ── Main ───────────────────────────────────────────────────────────────
def run():
    global _PASSED, _FAILED
    print(f"{'='*60}\nbasic_resolve  (root={ROOT})\n{'='*60}")
    _setup()
    test_single_package_no_deps()
    test_single_source_package()
    test_transitive_dependency()
    test_version_selection_latest()
    test_version_skip()
    print(f"\n  {_PASSED} passed, {_FAILED} failed")
    return _FAILED == 0


if __name__ == "__main__":
    sys.exit(0 if run() else 1)
