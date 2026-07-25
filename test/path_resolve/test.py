"""
path_resolve/test.py — Test path-based package resolution.

Tests RefPackage._assemble_path: when packages.json uses a "path" field
pointing to a fixture directory, IMakeCore should resolve it directly.
"""
import json, os, re, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
IMAKECORE_PY = ROOT / ".system" / "IMakeCore.py"
UPDATE_DB_PY = ROOT / ".system" / "scripts" / "updateDb.py"
FIXTURES = ROOT / ".lib"
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
        for m in re.finditer(r'include\((.+?)\)', txt):
            _check(Path(m.group(1)).exists(), f"{project.name}: broken include: {m.group(1)}")


def _vfy_cache(project: Path, *names: str):
    cache = project / ".data" / "resolve-cache.json"
    _check(cache.exists(), f"{project.name}: missing resolve-cache.json")
    if cache.exists():
        data = json.loads(cache.read_text(encoding="utf-8"))
        for n in names:
            _check(n in data.get("resolved", {}), f"{project.name}: cache missing '{n}'")


# ── Tests ──────────────────────────────────────────────────────────────

def test_path_resolve_header_only():
    """Resolve hello@1.0.0 by referencing its directory path directly."""
    fixture_path = str(FIXTURES / "test@hello@1.0.0")
    proj = _prepare(ROOT / "project_path", {
        "test/hello": {
            "version": "1.0.0",
            "path": fixture_path
        }
    })
    r = _run(proj)
    _check(r.returncode == 0, f"rc={r.returncode}\n{r.stdout[:300]}")
    _vfy_pri(proj, "hello")
    _vfy_cache(proj, "test/hello")

    # The .package.pri should include from the system lib or project lib
    pri = (proj / ".package.pri").read_text() if (proj / ".package.pri").exists() else ""
    _check("hello" in pri, "path-resolved hello missing from .package.pri")


def test_path_resolve_source_package():
    """Resolve hello@2.0.0 (source+cpp) via path."""
    fixture_path = str(FIXTURES / "test@hello@2.0.0")
    proj = _prepare(ROOT / "project_path_src", {
        "test/hello": {
            "version": "2.0.0",
            "path": fixture_path
        }
    })
    r = _run(proj)
    _check(r.returncode == 0, f"rc={r.returncode}\n{r.stdout[:300]}")
    _vfy_pri(proj, "hello")


def test_path_resolve_nonexistent():
    """Path that doesn't exist should fail."""
    proj = _prepare(ROOT / "project_path_bad", {
        "test/hello": {
            "version": "1.0.0",
            "path": str(ROOT / "nonexistent_dir")
        }
    })
    r = _run(proj)
    _check(r.returncode == 1, f"expected failure for bad path, got {r.returncode}")
    out = (r.stdout + r.stderr).lower()
    _check(any(w in out for w in ("does not exist", "cannot", "error", "not found", "failed")),
           f"missing error for nonexistent path: {out[:200]}")


# ── Main ───────────────────────────────────────────────────────────────
def run():
    global _PASSED, _FAILED
    print(f"{'='*60}\npath_resolve  (root={ROOT})\n{'='*60}")
    _setup()
    test_path_resolve_header_only()
    test_path_resolve_source_package()
    test_path_resolve_nonexistent()
    print(f"\n  {_PASSED} passed, {_FAILED} failed")
    return _FAILED == 0


if __name__ == "__main__":
    sys.exit(0 if run() else 1)
