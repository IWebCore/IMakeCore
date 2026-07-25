"""
version_specifiers/test.py — Test all version specifier patterns.
"""
import json, os, re, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
IMAKECORE_PY = ROOT / ".system" / "IMakeCore.py"
UPDATE_DB_PY = ROOT / ".system" / "updateDb.py"
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

def test_wildcard_latest():
    """'*' should resolve to the latest available version (2.0.0)."""
    proj = _prepare(ROOT / "project_wildcard", {"test/hello": "*"})
    r = _run(proj)
    _check(r.returncode == 0, f"rc={r.returncode}\n{r.stdout[:300]}")
    _vfy_pri(proj, "hello")
    _vfy_cache(proj, "test/hello")
    # Should pick latest = 2.0.0
    pri_txt = (proj / ".package.pri").read_text() if (proj / ".package.pri").exists() else ""
    _check("2.0.0" in pri_txt, "wildcard should pick 2.0.0 latest")


def test_exact_version():
    """Exact '2.0.0' should resolve to that specific version."""
    proj = _prepare(ROOT / "project_exact", {"test/hello": "2.0.0"})
    r = _run(proj)
    _check(r.returncode == 0, f"rc={r.returncode}")
    pri_txt = (proj / ".package.pri").read_text() if (proj / ".package.pri").exists() else ""
    _check("2.0.0" in pri_txt, "exact 2.0.0 not found")
    _check("1.0.0" not in pri_txt, "1.0.0 leaked into exact match")


def test_version_range_lower_bound():
    """'>=1.0' should resolve to the latest (2.0.0)."""
    proj = _prepare(ROOT / "project_range_low", {"test/hello": ">=1.0"})
    r = _run(proj)
    _check(r.returncode == 0, f"rc={r.returncode}")
    pri_txt = (proj / ".package.pri").read_text() if (proj / ".package.pri").exists() else ""
    _check("2.0.0" in pri_txt, ">=1.0 should pick 2.0.0")


def test_version_range_restricted():
    """'>=1.0,<2.0' should pick 1.0.0 since 2.0.0 is excluded."""
    proj = _prepare(ROOT / "project_range_restricted", {"test/hello": ">=1.0,<2.0"})
    r = _run(proj)
    _check(r.returncode == 0, f"rc={r.returncode}")
    pri_txt = (proj / ".package.pri").read_text() if (proj / ".package.pri").exists() else ""
    _check("1.0.0" in pri_txt, ">=1.0,<2.0 should pick 1.0.0")
    _check("2.0.0" not in pri_txt, "2.0.0 should be excluded by <2.0")


def test_version_skip_x():
    """Version 'x' (any case) should skip."""
    proj = _prepare(ROOT / "project_skip", {"test/hello": "x"})
    r = _run(proj)
    _check(r.returncode == 0, f"rc={r.returncode}")
    if (proj / ".package.pri").exists():
        _check("hello" not in (proj / ".package.pri").read_text(), "x should skip")


# ── Main ───────────────────────────────────────────────────────────────
def run():
    global _PASSED, _FAILED
    print(f"{'='*60}\nversion_specifiers  (root={ROOT})\n{'='*60}")
    _setup()
    test_wildcard_latest()
    test_exact_version()
    test_version_range_lower_bound()
    test_version_range_restricted()
    test_version_skip_x()
    print(f"\n  {_PASSED} passed, {_FAILED} failed")
    return _FAILED == 0


if __name__ == "__main__":
    sys.exit(0 if run() else 1)
