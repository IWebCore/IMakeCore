"""Final fix: rebuild run() for each test.py from its test functions only."""
import pathlib, re

RUN_TEMPLATE = '''
def run(pack_type: str = "qmake"):
    global _PASSED, _FAILED, _G_PACK_TYPE
    _G_PACK_TYPE = pack_type
    print(f"{'='*60}\\n{SUITE}  (root={ROOT})\\n{'='*60}")
    _setup()
{CALLS}
    print(f"\\n  {_PASSED} passed, {_FAILED} failed")
    return _FAILED == 0
'''

for f in pathlib.Path("C:/Users/Yue/IMakeCore/test").rglob("test.py"):
    content = f.read_text(encoding="utf-8")
    suite = f.parent.name

    # Find ALL test function names in the file
    test_funcs = re.findall(r'def (test_\w+)\(\)', content)
    calls = "\n".join(f"    {n}()" for n in sorted(set(test_funcs)))

    # Find the old run() function boundaries
    old_run_start = content.find("\ndef run(")
    if old_run_start < 0:
        old_run_start = content.find("def run(")

    if old_run_start > 0:
        # Replace from run() to end of file
        new_run = RUN_TEMPLATE.replace("{SUITE}", suite).replace("{CALLS}", calls)
        result = content[:old_run_start].rstrip() + "\n\n" + new_run.strip() + "\n"
        # Add main block
        result += '\n\nif __name__ == "__main__":\n    pt = sys.argv[1] if len(sys.argv) > 1 else "qmake"\n    sys.exit(0 if run(pt) else 1)\n'
        f.write_text(result, encoding="utf-8")
        print(f"{suite}: {len(set(test_funcs))} tests in run()")
