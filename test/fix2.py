"""Clone basic_resolve structure to all other test.py files."""
import pathlib, re

BASE = pathlib.Path("C:/Users/Yue/IMakeCore/test/basic_resolve/test.py").read_text(encoding="utf-8")

# Extract the template header (everything before test functions)
test_header_end = BASE.find("def test_single_package_no_deps")
template_header = BASE[:test_header_end]

# Extract the run/main footer
run_start = BASE.find("def run(pack_type")
template_footer = BASE[run_start:]

for f in pathlib.Path("C:/Users/Yue/IMakeCore/test").rglob("test.py"):
    if f.parent.name == "basic_resolve":
        continue  # already fixed

    content = f.read_text(encoding="utf-8")
    suite = f.parent.name

    # Find test functions in old file
    test_funcs = re.findall(r'(def test_\w+\(\):.*?)(?=\n\ndef |\n# --|\Z)', content, re.DOTALL)
    if not test_funcs:
        test_funcs = re.findall(r'(def test_\w+\(\):.*?)(?=\ndef |\Z)', content, re.DOTALL)

    test_section = "\n\n".join(t.strip() for t in test_funcs)

    # Find test call names from old run()
    run_match = re.search(r'def run.*?\n(.*?)(?=    print|\n    return)', content, re.DOTALL)
    test_names = []
    if run_match:
        test_names = re.findall(r'(test_\w+)\(\)', run_match.group(1))

    if not test_names and test_funcs:
        test_names = re.findall(r'def (test_\w+)', "\n".join(test_funcs))

    # Build new content
    new_footer = template_footer.replace("basic_resolve", suite)
    # Replace test calls in run()
    old_calls = re.findall(r'    (test_\w+)\(\)', new_footer)
    i = 0
    for old_name in old_calls:
        if i < len(test_names):
            new_footer = new_footer.replace(f"    {old_name}()", f"    {test_names[i]}()", 1)
            i += 1

    result = template_header + "\n" + test_section + "\n\n" + new_footer
    f.write_text(result.strip() + "\n", encoding="utf-8")
    print(f"{suite}: {len(test_names)} tests")
