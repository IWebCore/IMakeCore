"""Fix all test.py files — add pack_type parameter support."""
import pathlib, re

TEMPLATE_TOP = '''import json, os, re, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
IMAKECORE_PY = ROOT / ".system" / "IMakeCore.py"
UPDATE_DB_PY = ROOT / ".system" / "updateDb.py"
FIXTURES = ROOT / ".lib"
_PASSED = _FAILED = 0
_G_PACK_TYPE = "qmake"


def _setup():
    (ROOT / ".db").mkdir(exist_ok=True)
    subprocess.run([sys.executable, "-B", str(UPDATE_DB_PY)],
                   env={**os.environ, "IMAKECORE_ROOT": str(ROOT)},
                   capture_output=True, text=True, check=True, timeout=60)


def _run(project: Path, pack_type: str = None):
    if pack_type is None:
        pack_type = _G_PACK_TYPE
    return subprocess.run([sys.executable, "-B", str(IMAKECORE_PY), str(project), pack_type],
                          env={**os.environ, "IMAKECORE_ROOT": str(ROOT)},
                          capture_output=True, text=True, timeout=120)


def _prepare(project: Path, packages: dict) -> Path:
    for name in (".package.pri", ".package.cmake", ".data", ".lib", ".support", ".bin"):
        p = project / name
        if p.exists():
            (shutil.rmtree if p.is_dir() else os.remove)(str(p))
    project.mkdir(parents=True, exist_ok=True)
    (project / "packages.json").write_text(
        json.dumps({"packages": packages}), encoding="utf-8")
    return project


def _check(c, msg):
    global _PASSED, _FAILED
    if c: _PASSED += 1
    else: _FAILED += 1; print(f"  FAIL: {msg}")


'''

BOTTOM = '''
def run(pack_type: str = "qmake"):
    global _PASSED, _FAILED, _G_PACK_TYPE
    _G_PACK_TYPE = pack_type
    print("=" * 60)
    print("{SUITE}  (root=" + str(ROOT) + ")")
    print("=" * 60)
    _setup()
{CALLS}
    print("")
    print(f"  {_PASSED} passed, {_FAILED} failed")
    return _FAILED == 0


if __name__ == "__main__":
    pt = sys.argv[1] if len(sys.argv) > 1 else "qmake"
    sys.exit(0 if run(pt) else 1)
'''

for f in pathlib.Path("C:/Users/Yue/IMakeCore/test").rglob("test.py"):
    content = f.read_text(encoding="utf-8")
    suite = f.parent.name

    # Extract helpers: everything between _check and first test_
    check_pos = content.find("def _check")
    if check_pos < 0: continue
    after_check = content[check_pos:]
    test_pos = after_check.find("\ndef test_")
    if test_pos < 0: test_pos = after_check.find("def test_")
    if test_pos < 0: continue
    helpers = after_check[:test_pos].strip()

    # Extract test section
    test_section_start = check_pos + test_pos
    run_pos = content.find("\ndef run(", test_section_start)
    if run_pos < 0: run_pos = content.find("def run(", test_section_start)
    if run_pos > 0:
        tests = content[test_section_start:run_pos].strip()
    else:
        tests = content[test_section_start:].strip()

    # Extract test function names
    test_names = re.findall(r'def (test_\w+)', tests)
    calls = "\n".join(f"    {n}()" for n in test_names)

    result = TEMPLATE_TOP + helpers + "\n\n" + tests + "\n\n"
    result += BOTTOM.replace("{SUITE}", suite).replace("{CALLS}", calls)

    f.write_text(result.strip() + "\n", encoding="utf-8")
    print(f"{suite}: {len(test_names)} tests")
