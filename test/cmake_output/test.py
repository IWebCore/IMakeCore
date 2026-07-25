"""
cmake_output/test.py — Test CMake output generation (.package.cmake).
"""
import json, os, re, shutil, subprocess, sys
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


def _run_cmake(project: Path):
    return subprocess.run([sys.executable, "-B", str(IMAKECORE_PY), str(project), "cmake"],
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


def _vfy_cmake(project: Path, *expected: str):
    cmake = project / ".package.cmake"
    _check(cmake.exists(), f"{project.name}: missing .package.cmake")
    if cmake.exists():
        txt = cmake.read_text()
        for pkg in expected:
            _check(pkg in txt, f"{project.name}: .package.cmake missing '{pkg}'")
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

def test_cmake_single_package():
    proj = _prepare(ROOT / "project_cmake_single", {"test/hello": "1.0.0"})
    r = _run_cmake(proj)
    _check(r.returncode == 0, f"rc={r.returncode}\n{r.stdout[:300]}")
    _vfy_cmake(proj, "hello")
    _vfy_cache(proj, "test/hello")


def test_cmake_transitive():
    proj = _prepare(ROOT / "project_cmake_trans", {"test/world": "1.0.0"})
    r = _run_cmake(proj)
    _check(r.returncode == 0, f"rc={r.returncode}")
    _vfy_cmake(proj, "hello", "world")
    _vfy_cache(proj, "test/hello", "test/world")


def test_cmake_version_select():
    proj = _prepare(ROOT / "project_cmake_ver", {"test/hello": ">=2.0"})
    r = _run_cmake(proj)
    _check(r.returncode == 0, f"rc={r.returncode}")
    txt = (proj / ".package.cmake").read_text() if (proj / ".package.cmake").exists() else ""
    _check("2.0.0" in txt, "cmake: 2.0.0 not selected")
    _check("1.0.0" not in txt, "cmake: 1.0.0 leaked")


# ── Main ───────────────────────────────────────────────────────────────
def run():
    global _PASSED, _FAILED
    print(f"{'='*60}\ncmake_output  (root={ROOT})\n{'='*60}")
    _setup()
    test_cmake_single_package()
    test_cmake_transitive()
    test_cmake_version_select()
    print(f"\n  {_PASSED} passed, {_FAILED} failed")
    return _FAILED == 0


if __name__ == "__main__":
    sys.exit(0 if run() else 1)
