"""
updateDb.py — Scan system package directories and populate package.db.
Usage: python -B .system/scripts/updateDb.py
"""
import os
import sys

_script_dir = os.path.dirname(os.path.abspath(__file__))
_system_dir = os.path.dirname(_script_dir)
if _system_dir not in sys.path:
    sys.path.insert(0, _system_dir)

from scripts.data.models import Base, get_engine, get_session
from scripts.data.models import LibPackageTable, LibPackageDetailTable
from scripts.data.GlobalData import GlobalData
from scripts.util.PackageScanner import PackageScanner
from scripts.Utils import Utils


class UpdateDb:
    def __init__(self):
        self.global_data = GlobalData()
        self.engine = get_engine()
        self.total_packages = 0

    def run(self):
        print("=" * 60)
        print("IMakeCore updateDb — Rebuilding package database")
        print("=" * 60)

        libstores = self.global_data.get_libstores()
        if not libstores:
            print("ERROR: No system libstores found. Check IMAKECORE_ROOT and config.json.")
            sys.exit(1)

        print(f"\nSystem libstores to scan ({len(libstores)}):")
        for ls in libstores:
            print(f"  - {ls}")

        self._rebuild_tables()
        self._scan_libstores(libstores)

        print(f"\n{'=' * 60}")
        print(f"Done. {self.total_packages} packages indexed.")
        print(f"Database: {self.engine.url}")
        print(f"{'=' * 60}")

    def _rebuild_tables(self):
        Base.metadata.drop_all(self.engine)
        Base.metadata.create_all(self.engine)
        print("\nDatabase cleared and recreated.")

    def _scan_libstores(self, libstores):
        session = get_session()
        try:
            for libstore in libstores:
                print(f"\nScanning: {libstore}")
                if not os.path.isdir(libstore):
                    print(f"  [SKIP] Not a directory.")
                    continue
                try:
                    entries = os.listdir(libstore)
                except PermissionError:
                    print(f"  [SKIP] Permission denied.")
                    continue

                for entry in entries:
                    package_dir = os.path.join(libstore, entry)
                    if not os.path.isdir(package_dir):
                        continue
                    package_json = os.path.join(package_dir, "package.json")
                    if not os.path.exists(package_json):
                        continue
                    self._index_package(session, package_dir, package_json)

            session.commit()
        except Exception as e:
            session.rollback()
            print(f"\nERROR: {e}")
            raise
        finally:
            session.close()

    def _index_package(self, session, package_dir, package_json):
        try:
            pkg_data = Utils.loadJson(package_json)
        except Exception as e:
            print(f"  [WARN] Failed to read {package_json}: {e}")
            return

        name = pkg_data.get("name", "")
        publisher = pkg_data.get("publisher", "")
        version = pkg_data.get("version", "")

        if not name or not version:
            print(f"  [WARN] Invalid package.json: {package_dir}")
            return

        lib_pkg = LibPackageTable(
            publisher=publisher,
            name=name,
            is_global=pkg_data.get("isGlobal", True),
            version=version,
            summary=pkg_data.get("summary", ""),
            mode=pkg_data.get("mode", "sources"),
            path=os.path.normpath(package_dir),
            dependencies=[
                {"name": k, "version": v}
                for k, v in pkg_data.get("dependencies", {}).items()
            ],
        )
        session.add(lib_pkg)

        scanner = PackageScanner(package_dir, pkg_data.get("resolve"))
        scan_result = scanner.scan()

        detail = LibPackageDetailTable.from_scan_result(
            scan_result, os.path.normpath(package_dir), name, publisher, version)
        session.add(detail)

        self.total_packages += 1
        ignore_count = len(pkg_data.get("resolve", {}).get("ignore", []))
        print(f"  [OK] {publisher}/{name}@{version}"
              f" (headers={len(scan_result.headers)},"
              f" sources={len(scan_result.sources)},"
              f" includes={len(scan_result.includes)},"
              f" ignores={ignore_count})")


def main():
    UpdateDb().run()


if __name__ == "__main__":
    main()
