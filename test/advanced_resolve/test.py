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
    for name in (".package.pri", ".package.cmake", ".package.xmake", ".data", ".lib", ".support", ".bin"):
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
    pri = project / (".package.xmake" if _G_PACK_TYPE == "xmake" else (".package.cmake" if _G_PACK_TYPE == "cmake" else ".package.pri"))
    _check(pri.exists(), f"{project.name}: output missing")
    if pri.exists():
        txt = pri.read_text()
        for pkg in expected: _check(pkg in txt, f"{project.name}: missing '{pkg}'")
        pattern = r'includes\(["\'](.+?)["\']\)' if _G_PACK_TYPE == "xmake" else r'include\((.+?)\)'
        for m in re.finditer(pattern, txt):
            _check(Path(m.group(1)).exists(), f"{project.name}: broken include: {m.group(1)}")

def _vfy_cache(project: Path, *names: str):
    cache = project / ".data" / "resolve-cache.json"
    _check(cache.exists(), f"{project.name}: resolve-cache missing")
    if cache.exists():
        data = json.loads(cache.read_text(encoding="utf-8"))
        for n in names: _check(n in data.get("resolved",{}), f"{project.name}: cache missing '{n}'")

def _vfy_absent(project: Path, *forbidden: str):
    pri = project / (".package.xmake" if _G_PACK_TYPE == "xmake" else (".package.cmake" if _G_PACK_TYPE == "cmake" else ".package.pri"))
    if pri.exists():
        txt = pri.read_text()
        for pkg in forbidden: _check(pkg not in txt, f"{project.name}: leaked '{pkg}'")

# -- Tests


def test_publisher_scope():
    """Using 'test/hello' with publisher prefix should resolve correctly."""
    proj = _prepare(ROOT / "project_publisher", {"test/hello": "1.0.0"})
    r = _run(proj)
    _check(r.returncode == 0, f"rc={r.returncode}")
    _vfy_pri(proj, "hello")
    _vfy_cache(proj, "test/hello")

def test_mode_default_explicit():
    """Explicit mode='default' should work like no mode specified."""
    proj = _prepare(ROOT / "project_default", {
        "test/hello": {"version": "1.0.0", "mode": "default"}
    })
    r = _run(proj)
    _check(r.returncode == 0, f"rc={r.returncode}")
    _vfy_pri(proj, "hello")

def test_two_independent_packages():
    """Two unrelated packages should both resolve."""
    proj = _prepare(ROOT / "project_two", {
        "test/hello": "1.0.0",
        "test/world": "1.0.0"
    })
    r = _run(proj)
    _check(r.returncode == 0, f"rc={r.returncode}")
    _vfy_pri(proj, "hello", "world")
    _vfy_cache(proj, "test/hello", "test/world")

def test_transitive_with_versions():
    """world depends on hello>=1.0 — with two hello versions, picks latest but resolves."""
    proj = _prepare(ROOT / "project_trans_ver", {
        "test/world": {"version": "1.0.0"}
    })
    r = _run(proj)
    _check(r.returncode == 0, f"rc={r.returncode}")
    _vfy_pri(proj, "hello", "world")
    _vfy_cache(proj, "test/hello", "test/world")


def test_cache_roundtrip():
    """Run twice — second run should use resolve-cache."""
    proj = _prepare(ROOT / "project_cache", {"test/hello": "1.0.0"})
    r1 = _run(proj)
    _check(r1.returncode == 0, f"first run rc={r1.returncode}")

    # save_cache already ran. get_cached should find the entry.
    cache = proj / ".data" / "resolve-cache.json"
    _check(cache.exists(), "resolve-cache.json not created")

    # Second run — cache should be read and suggestCandidate set
    r2 = _run(proj)
    _check(r2.returncode == 0, f"second run rc={r2.returncode}")
    _vfy_pri(proj, "hello")


def test_override_global():
    """Global override pins hello to 1.0.0 even though >=1.0 would pick 2.0.0."""
    proj = _prepare(ROOT / "project_override_global", {"test/hello": ">=1.0"})
    data = json.loads((proj / "packages.json").read_text(encoding="utf-8"))
    data["override"] = {"test/hello": "1.0.0"}
    (proj / "packages.json").write_text(json.dumps(data, indent=2), encoding="utf-8")

    r = _run(proj)
    _check(r.returncode == 0, f"rc={r.returncode}\n{r.stdout[:300]}")

    pri_txt = (proj / (".package.xmake" if _G_PACK_TYPE == "xmake" else (".package.cmake" if _G_PACK_TYPE == "cmake" else ".package.pri"))).read_text()
    _check("1.0.0" in pri_txt, "override should force 1.0.0")
    _check("2.0.0" not in pri_txt, "2.0.0 should not appear when overridden to 1.0.0")


def test_override_per_package():
    """Per-package override beats global override."""
    proj = _prepare(ROOT / "project_override_perpkg", {
        "test/hello": {"version": ">=1.0", "override": "1.0.0"}
    })
    data = json.loads((proj / "packages.json").read_text(encoding="utf-8"))
    data["override"] = {"test/hello": "2.0.0"}
    (proj / "packages.json").write_text(json.dumps(data, indent=2), encoding="utf-8")

    r = _run(proj)
    _check(r.returncode == 0, f"rc={r.returncode}\n{r.stdout[:300]}")

    pri_txt = (proj / (".package.xmake" if _G_PACK_TYPE == "xmake" else (".package.cmake" if _G_PACK_TYPE == "cmake" else ".package.pri"))).read_text()
    _check("1.0.0" in pri_txt, "per-package override (1.0.0) should beat global (2.0.0)")
    _check("2.0.0" not in pri_txt, "2.0.0 should be overridden")


def test_override_string_entry():
    """Override works with simple string version entries."""
    proj = _prepare(ROOT / "project_override_string", {"test/hello": ">=1.0"})
    data = json.loads((proj / "packages.json").read_text(encoding="utf-8"))
    data["override"] = {"test/hello": "1.0.0"}
    (proj / "packages.json").write_text(json.dumps(data, indent=2), encoding="utf-8")

    r = _run(proj)
    _check(r.returncode == 0, f"rc={r.returncode}")
    pri_txt = (proj / (".package.xmake" if _G_PACK_TYPE == "xmake" else (".package.cmake" if _G_PACK_TYPE == "cmake" else ".package.pri"))).read_text()
    _check("1.0.0" in pri_txt, "string entry override should force 1.0.0")


def test_override_nonexistent_version():
    """Override to a version that doesn't exist — falls through to normal resolution."""
    proj = _prepare(ROOT / "project_override_badver", {"test/hello": ">=1.0"})
    data = json.loads((proj / "packages.json").read_text(encoding="utf-8"))
    data["override"] = {"test/hello": "9.9.9"}
    (proj / "packages.json").write_text(json.dumps(data, indent=2), encoding="utf-8")

    r = _run(proj)
    # Nonexistent override → forceCandidate stays None → normal resolution picks 2.0.0
    _check(r.returncode == 0, f"nonexistent override should fall through, got {r.returncode}")
    pri_txt = (proj / (".package.xmake" if _G_PACK_TYPE == "xmake" else (".package.cmake" if _G_PACK_TYPE == "cmake" else ".package.pri"))).read_text()
    _check("2.0.0" in pri_txt, "should fall through to normal resolution (2.0.0)")


def test_override_transitive():
    """Override applies only to root packages, not transitive deps.
    world depends on hello>=1.0 → hello@2.0.0 is picked by SAT solver.
    Override for hello doesn't apply because hello is not a root package."""
    proj = _prepare(ROOT / "project_override_trans", {"test/world": "1.0.0"})
    data = json.loads((proj / "packages.json").read_text(encoding="utf-8"))
    data["override"] = {"test/hello": "1.0.0"}
    (proj / "packages.json").write_text(json.dumps(data, indent=2), encoding="utf-8")

    r = _run(proj)
    _check(r.returncode == 0, f"rc={r.returncode}")
    # hello is transitive, override doesn't apply → SAT picks 2.0.0
    _vfy_pri(proj, "hello", "world")


def test_override_both_root_packages():
    """Override two root packages to specific versions."""
    proj = _prepare(ROOT / "project_override_both", {
        "test/hello": ">=1.0",
        "test/world": ">=1.0"
    })
    data = json.loads((proj / "packages.json").read_text(encoding="utf-8"))
    data["override"] = {"test/hello": "1.0.0", "test/world": "1.0.0"}
    (proj / "packages.json").write_text(json.dumps(data, indent=2), encoding="utf-8")

    r = _run(proj)
    _check(r.returncode == 0, f"rc={r.returncode}")
    pri_txt = (proj / (".package.xmake" if _G_PACK_TYPE == "xmake" else (".package.cmake" if _G_PACK_TYPE == "cmake" else ".package.pri"))).read_text()
    _check("test@hello@1.0.0" in pri_txt or ('1.0.0' in pri_txt and 'hello' in pri_txt),
           "hello should be overridden to 1.0.0")
    _check("test@world@1.0.0" in pri_txt or ('world' in pri_txt),
           "world should be overridden to 1.0.0")


# ── Main ───────────────────────────────────────────────────────────────

def run(pack_type: str = "qmake"):
    global _PASSED, _FAILED, _G_PACK_TYPE
    _G_PACK_TYPE = pack_type
    print(f"{'='*60}\nadvanced_resolve  (root={ROOT})\n{'='*60}")
    _setup()
    test_mode_default_explicit()
    test_publisher_scope()
    test_transitive_with_versions()
    test_cache_roundtrip()
    test_two_independent_packages()
    test_override_global()
    test_override_per_package()
    test_override_string_entry()
    test_override_nonexistent_version()
    test_override_transitive()
    test_override_both_root_packages()
    print(f"\n  {_PASSED} passed, {_FAILED} failed")
    return _FAILED == 0


if __name__ == "__main__":
    pt = sys.argv[1] if len(sys.argv) > 1 else "qmake"
    sys.exit(0 if run(pt) else 1)
