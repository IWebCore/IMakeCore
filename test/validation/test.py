"""basic_resolve/test.py"""
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
        if p.exists(): (shutil.rmtree if p.is_dir() else os.remove)(str(p))
    project.mkdir(parents=True, exist_ok=True)
    (project / "packages.json").write_text(json.dumps({"packages": packages}), encoding="utf-8")
    return project

def _check(c, msg):
    global _PASSED, _FAILED
    if c: _PASSED += 1
    else: _FAILED += 1; print(f"  FAIL: {msg}")

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
    _check(cache.exists(), f"{project.name}: resolve-cache missing")
    if cache.exists():
        data = json.loads(cache.read_text(encoding="utf-8"))
        for n in names: _check(n in data.get("resolved",{}), f"{project.name}: cache missing '{n}'")

def _vfy_absent(project: Path, *forbidden: str):
    pri = project / (".package.cmake" if _G_PACK_TYPE == "cmake" else ".package.pri")
    if pri.exists():
        txt = pri.read_text()
        for pkg in forbidden: _check(pkg not in txt, f"{project.name}: leaked '{pkg}'")

def _out(r): return (r.stdout + r.stderr).lower()

# -- Tests


def test_header_only_rejects_static():
    """hello@1.0.0 (header-only) + static → error."""
    proj = _prepare(ROOT / "project_err_static",
                    {"test/hello": {"version": "1.0.0", "mode": "static"}})
    r = _run(proj)
    _check(r.returncode == 1, f"expected exit(1), got {r.returncode}")
    _check("header-only" in _out(r), f"missing 'header-only': {_out(r)[:200]}")
    _vfy_absent(proj)

def test_header_only_rejects_dynamic():
    """hello@1.0.0 (header-only) + dynamic → error."""
    proj = _prepare(ROOT / "project_err_dynamic",
                    {"test/hello": {"version": "1.0.0", "mode": "dynamic"}})
    r = _run(proj)
    _check(r.returncode == 1, f"expected exit(1), got {r.returncode}")
    _check("header-only" in _out(r), f"missing 'header-only': {_out(r)[:200]}")
    _vfy_absent(proj)

def test_missing_dependency():
    """Reference to nonexistent package → error, no .package.pri."""
    proj = _prepare(ROOT / "project_err_missing",
                    {"test/nonexistent": "1.0.0"})
    r = _run(proj)
    _check(r.returncode == 1, f"expected exit(1), got {r.returncode}")
    _check(any(w in _out(r) for w in ("cannot", "not found", "not in the resolved", "failed")),
           f"missing error indicator: {_out(r)[:200]}")
    _vfy_absent(proj)

def test_missing_packages_json():
    """No packages.json — should fail gracefully, no crash."""
    proj = ROOT / "project_no_pkg"
    for name in (".package.pri", ".package.cmake", ".data", ".lib", ".support", ".bin"):
        p = proj / name
        if p.exists():
            (shutil.rmtree if p.is_dir() else os.remove)(str(p))
    proj.mkdir(parents=True, exist_ok=True)
    r = _run(proj)
    _check(r.returncode in (0, 1), f"unexpected rc={r.returncode}")
    _check(not (proj / ".package.pri").exists() or r.returncode != 0,
           ".package.pri should not be generated when packages.json is missing")


def test_bare_name_publisher_not_found():
    """Package name without publisher that doesn't exist in DB — should fail."""
    proj = _prepare(ROOT / "project_bare_name", {"unknown_pkg": "1.0.0"})
    r = _run(proj)
    _check(r.returncode == 1, f"expected error, got {r.returncode}")
    out = _out(r)
    _check(any(w in out for w in ("cannot", "not found", "not in the resolved", "cannot resolve")),
           f"missing error: {out[:200]}")

def test_dynamic_without_definition():
    """dynamic mode without dynamicDefinition in resolve."""
    proj = _prepare(ROOT / "project_err_dynamic",
                    {"test/dynamic_lib": {"version": "1.0.0", "mode": "dynamic"}})
    r = _run(proj)
    _check(r.returncode in (0, 1), f"unexpected rc={r.returncode}")
    if r.returncode == 1:
        _check("dynamic" in _out(r), f"missing 'dynamic' in error: {_out(r)[:200]}")


# ── Main ───────────────────────────────────────────────────────────────

def run(pack_type: str = "qmake"):
    global _PASSED, _FAILED, _G_PACK_TYPE
    _G_PACK_TYPE = pack_type
    print(f"{'='*60}\nvalidation  (root={ROOT})\n{'='*60}")
    _setup()
    test_dynamic_without_definition()
    test_header_only_rejects_dynamic()
    test_header_only_rejects_static()
    test_missing_dependency()
    test_missing_packages_json()
    test_bare_name_publisher_not_found()
    print(f"\n  {_PASSED} passed, {_FAILED} failed")
    return _FAILED == 0


if __name__ == "__main__":
    pt = sys.argv[1] if len(sys.argv) > 1 else "qmake"
    sys.exit(0 if run(pt) else 1)
