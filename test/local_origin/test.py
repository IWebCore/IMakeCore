"""basic_resolve/test.py"""
import json, os, re, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
IMAKECORE_PY = ROOT / ".system" / "IMakeCore.py"
UPDATE_DB_PY = ROOT / ".system" / "updateDb.py"
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

# -- Tests


def test_local_origin_copies_package():
    """origin=local should copy the resolved package into project/.lib/"""
    proj = _prepare(ROOT / "project_local", {
        "test/hello": {"version": "1.0.0", "origin": "local"}
    })
    r = _run(proj)
    _check(r.returncode == 0, f"rc={r.returncode}\n{r.stdout[:300]}")

    _vfy_pri(proj, "hello")
    _vfy_cache(proj, "test/hello")

    # Check that the package was copied to project .lib/
    proj_lib = proj / ".lib"
    _check(proj_lib.exists(), "project .lib/ should exist after local origin")
    if proj_lib.exists():
        # Should have test@hello@1.0.0 or similar in .lib/
        hello_dirs = list(proj_lib.glob("*hello*"))
        _check(len(hello_dirs) > 0, "hello package not copied to project .lib/")

    # .package.pri should reference the project-local .lib/ path
    pri = proj / ".package.pri"
    if pri.exists():
        txt = pri.read_text()
        _check(str(proj_lib).replace("\\", "/") in txt.replace("\\", "/"),
               ".package.pri should reference project-local .lib/")

def test_local_origin_without_system_package():
    """origin=local for a nonexistent package should fail."""
    proj = _prepare(ROOT / "project_local_missing", {
        "test/nonexistent": {"version": "1.0.0", "origin": "local"}
    })
    r = _run(proj)
    _check(r.returncode == 1, f"expected failure for missing local package, got {r.returncode}")
    out = (r.stdout + r.stderr).lower()
    _check(any(w in out for w in ("cannot", "not found", "failed")),
           f"missing error for nonexistent local: {out[:200]}")

def test_local_origin_already_in_local():
    """origin=local when package already exists in local .lib/ — use existing."""
    # First, create a project that copies hello to its .lib/
    proj1 = _prepare(ROOT / "project_local_first", {
        "test/hello": {"version": "1.0.0", "origin": "local"}
    })
    r1 = _run(proj1)
    _check(r1.returncode == 0, f"first run failed: rc={r1.returncode}")

    # Second run with same config — should find it already local
    proj2 = _prepare(ROOT / "project_local_second", {
        "test/hello": {"version": "1.0.0", "origin": "local"}
    })
    r2 = _run(proj2)
    _check(r2.returncode == 0, f"second run failed: rc={r2.returncode}")
    _vfy_pri(proj2, "hello")


# ── Main ───────────────────────────────────────────────────────────────

def run(pack_type: str = "qmake"):
    global _PASSED, _FAILED, _G_PACK_TYPE
    _G_PACK_TYPE = pack_type
    print(f"{'='*60}\nlocal_origin  (root={ROOT})\n{'='*60}")
    _setup()
    test_local_origin_already_in_local()
    test_local_origin_copies_package()
    test_local_origin_without_system_package()
    print(f"\n  {_PASSED} passed, {_FAILED} failed")
    return _FAILED == 0


if __name__ == "__main__":
    pt = sys.argv[1] if len(sys.argv) > 1 else "qmake"
    sys.exit(0 if run(pt) else 1)
