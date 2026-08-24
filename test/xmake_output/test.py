"""xmake_output/test.py"""
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
    for name in (".package.pri", ".package.cmake", ".package.lua", ".data", ".lib", ".support", ".bin"):
        p = project / name
        if p.exists(): (shutil.rmtree if p.is_dir() else os.remove)(str(p))
    project.mkdir(parents=True, exist_ok=True)
    (project / "packages.json").write_text(json.dumps({"packages": packages}), encoding="utf-8")
    return project

def _check(c, msg):
    global _PASSED, _FAILED
    if c: _PASSED += 1
    else: _FAILED += 1; print(f"  FAIL: {msg}")

def _out(project: Path) -> Path:
    return project / (".package.lua" if _G_PACK_TYPE == "xmake" else (".package.cmake" if _G_PACK_TYPE == "cmake" else ".package.pri"))

def _norm(p: str) -> str:
    return os.path.normpath(p).replace(os.sep, "/")

def _vfy_pri(project: Path, *expected: str):
    pri = _out(project)
    _check(pri.exists(), f"{project.name}: output missing")
    if pri.exists():
        txt = pri.read_text(encoding="utf-8")
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
    pri = _out(project)
    if pri.exists():
        txt = pri.read_text(encoding="utf-8")
        for pkg in forbidden: _check(pkg not in txt, f"{project.name}: leaked '{pkg}'")

# -- Tests


def test_xmake_single_package():
    proj = _prepare(ROOT / "project_xmake_single", {"test/hello": "1.0.0"})
    r = _run(proj)
    _check(r.returncode == 0, f"rc={r.returncode}\n{r.stdout[:300]}")
    _vfy_pri(proj, "hello")
    _vfy_cache(proj, "test/hello")
    if _G_PACK_TYPE == "xmake":
        txt = _out(proj).read_text(encoding="utf-8")
        _check("includes(" in txt, f"{proj.name}: missing includes(")
        pkg_xmake = proj / ".lib" / "test@hello@1.0.0.xmake"
        _check(pkg_xmake.exists(), f"{proj.name}: per-package .xmake missing")
        if pkg_xmake.exists():
            _check("add_includedirs(" in pkg_xmake.read_text(encoding="utf-8"), f"{proj.name}: missing add_includedirs(")

def test_xmake_transitive():
    proj = _prepare(ROOT / "project_xmake_trans", {"test/world": "1.0.0"})
    r = _run(proj)
    _check(r.returncode == 0, f"rc={r.returncode}")
    _vfy_pri(proj, "hello", "world")
    _vfy_cache(proj, "test/hello", "test/world")
    if _G_PACK_TYPE == "xmake":
        txt = _out(proj).read_text(encoding="utf-8")
        _check("includes(" in txt, f"{proj.name}: missing includes(")

def test_xmake_version_select():
    proj = _prepare(ROOT / "project_xmake_ver", {"test/hello": ">=2.0"})
    r = _run(proj)
    _check(r.returncode == 0, f"rc={r.returncode}")
    txt = _out(proj).read_text(encoding="utf-8")
    _check("2.0.0" in txt, "2.0.0 not selected")
    _check("1.0.0" not in txt, "1.0.0 leaked")

def test_xmake_static_link_contract():
    proj = _prepare(ROOT / "project_xmake_static", {"test/hello": {"version": "2.0.0", "mode": "static"}})
    r = _run(proj)
    _check(r.returncode == 0, f"rc={r.returncode}\n{r.stdout[:300]}")
    if _G_PACK_TYPE != "xmake":
        _vfy_pri(proj, "hello")
        return

    pkg_xmake = proj / ".lib" / "test@hello@2.0.0.xmake"
    sup_dir = proj / ".support" / "test@hello@2.0.0_static"
    sup_lua = sup_dir / "xmake.lua"
    _check(pkg_xmake.exists(), f"{proj.name}: per-package .xmake missing")
    _check(sup_lua.exists(), f"{proj.name}: support xmake.lua missing")
    if not (pkg_xmake.exists() and sup_lua.exists()):
        return

    pkg_txt = pkg_xmake.read_text(encoding="utf-8")
    sup_txt = sup_lua.read_text(encoding="utf-8")

    m_linkdir = re.search(r'add_linkdirs\("(.+?)"\)', pkg_txt)
    _check(m_linkdir is not None, f"{proj.name}: missing add_linkdirs(...)")
    _check('test@hello@2.0.0_static/$(arch)-$(os)-static' in sup_txt, f"{proj.name}: missing set_targetdir(...)")
    m_targetdir = re.search(r'set_targetdir\("(.+?)"\)', sup_txt)

    m_links = re.search(r'add_links\("(.+?)"\)', pkg_txt)
    m_basename = re.search(r'set_basename\("(.+?)"\)', sup_txt)
    _check(m_links is not None, f"{proj.name}: missing add_links(...)")
    _check(m_basename is not None, f"{proj.name}: missing set_basename(...)")
    if m_links and m_basename:
        _check(m_links.group(1) == m_basename.group(1),
               f"{proj.name}: safe_name mismatch: {m_links.group(1)} vs {m_basename.group(1)}")

    if m_linkdir and m_targetdir:
        pkg_dir = _norm(str(proj / ".lib"))
        # per-package add_linkdirs is "$(scriptdir)/../.support/<pkg>_static/..." where
        # its $(scriptdir) is the .lib/ store; the support lib's set_targetdir is an
        # absolute path to the same dir. Resolve the former and compare.
        linkdir_resolved = _norm(m_linkdir.group(1).replace("$(scriptdir)", pkg_dir))
        targetdir_resolved = _norm(m_targetdir.group(1))
        _check(linkdir_resolved == targetdir_resolved,
               f"{proj.name}: link/target dir mismatch: {linkdir_resolved} vs {targetdir_resolved}")


# ── Main ───────────────────────────────────────────────────────────────

def run(pack_type: str = "qmake"):
    global _PASSED, _FAILED, _G_PACK_TYPE
    _G_PACK_TYPE = pack_type
    print(f"{'='*60}\nxmake_output  (root={ROOT})\n{'='*60}")
    _setup()
    test_xmake_single_package()
    test_xmake_transitive()
    test_xmake_version_select()
    test_xmake_static_link_contract()
    print(f"\n  {_PASSED} passed, {_FAILED} failed")
    return _FAILED == 0


if __name__ == "__main__":
    pt = sys.argv[1] if len(sys.argv) > 1 else "qmake"
    sys.exit(0 if run(pt) else 1)
