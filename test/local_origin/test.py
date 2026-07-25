"""
local_origin/test.py — Test origin=local copies packages from system to project .lib/
"""
import json, os, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
IMAKECORE_PY = ROOT / ".system" / "IMakeCore.py"
UPDATE_DB_PY = ROOT / ".system" / "scripts" / "updateDb.py"
_PASSED = _FAILED = 0


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


def _vfy_pri(project: Path, *expected: str):
    pri = project / ".package.pri"
    _check(pri.exists(), f"{project.name}: missing .package.pri")
    if pri.exists():
        txt = pri.read_text()
        for pkg in expected:
            _check(pkg in txt, f"{project.name}: missing '{pkg}'")


def _vfy_cache(project: Path, *names: str):
    cache = project / ".data" / "resolve-cache.json"
    _check(cache.exists(), f"{project.name}: missing resolve-cache.json")
    if cache.exists():
        data = json.loads(cache.read_text(encoding="utf-8"))
        for n in names:
            _check(n in data.get("resolved", {}), f"{project.name}: cache missing '{n}'")


# ── Tests ──────────────────────────────────────────────────────────────

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
def run():
    global _PASSED, _FAILED
    print(f"{'='*60}\nlocal_origin  (root={ROOT})\n{'='*60}")
    _setup()
    test_local_origin_copies_package()
    test_local_origin_without_system_package()
    test_local_origin_already_in_local()
    print(f"\n  {_PASSED} passed, {_FAILED} failed")
    return _FAILED == 0


if __name__ == "__main__":
    sys.exit(0 if run() else 1)
