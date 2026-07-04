
import os
from packaging.version import *
from packaging.specifiers import *
from scripts.data.models import LibPackageTable
from scripts.Utils import Utils
from scripts.data.models import get_session

class LibPackage:

    @staticmethod
    def split_name(name):
        if "/" in name:
            parts = name.split("/", 1)
            return parts[0].strip(), parts[1].strip(), False
        return "", name.strip(), True

    class Dependency:
        def __init__(self, name:str, version:str):
            self.fullName = name
            self.version = version
            self.versionSpec = Utils.parseVersionSpecifier(version)
            
        def matchLib(self, libPackage):
            if "/" in self.fullName:
                return self.fullName == (libPackage.publisher + "/" + libPackage.name)  \
                        and self.versionSpec.contains(Version(libPackage.version))
            
            return self.fullName == libPackage.name     \
                    and self.versionSpec.contains(Version(libPackage.version))  \
                    and libPackage.isGlobal
                    
    def __init__(self):
        self.name : str = ""
        self.publisher : str = ""
        self.isGlobal : bool = False
        self.version : str = ""
        self.summary : str = ""
        self.autoScan : bool = False
        self.mode : str = "sources"
        self.path : str = ""
        self.dependencies : List[LibPackage.Dependency] = []
        self.success : bool = True
        self._supported_modes = ["source", "static"]

    def __init__(self, path:str):
        self.name : str = ""
        self.publisher : str = ""
        self.isGlobal : bool = False
        self.version : str = ""
        self.summary : str = ""
        self.autoScan : bool = False
        self.mode : str = "sources"
        self.path : str = path
        self.dependencies : List[LibPackage.Dependency] = []
        self.success : bool = True
        self._supported_modes = ["source", "static"]

        try:
            self.loadPackage()
        except:
            self.success = False

        if self.success:
            self.checkPackage()

    def __str__(self):
        return f"{self.fullName}@{self.version}"
    
    def loadPackage(self):
        path= os.path.join(self.path, "package.json")
        if not os.path.exists(path):
            self.success = False
            return
        
        self.json = Utils.loadJson(path)
        
        self.publisher = self.json.get("publisher", "")
        self.name = self.json.get("name")
        self.isGlobal = self.json.get("isGlobal", True)
        
        self.version = self.json.get("version")
        self.summary = self.json.get("summary")
        self.autoScan = False  # deprecated, always False
        self._supported_modes = ["source", "static"]
        raw_mode = self.json.get("mode")
        if raw_mode is not None:
            if isinstance(raw_mode, str):
                raw_mode = [raw_mode]
            for m in raw_mode:
                if m not in ("source", "static", "dynamic"):
                    print(f"ERROR: {self.name}: invalid mode '{m}' in package.json mode list")
                    exit(1)
            self._supported_modes = raw_mode if raw_mode else ["source", "static"]
        dependencies = self.json.get("dependencies", {})
        for key, value in dependencies.items():
            dep = LibPackage.Dependency(key, value)
            self.dependencies.append(dep)
    
    def checkPackage(self):
        if not self.isGlobal and self.publisher == "":
            self.success = False
            assert False, f"Invalid package.json, package {self.name} is not global and publisher is missing. Path:{self.path}"
            
        assert self.name and self.version, f"Invalid package.json, package name or version is missing. Path:{self.path}"

    @classmethod
    def from_db_row(cls, row):
        """Create a LibPackage instance from a LibPackageTable ORM row."""
        lp = cls.__new__(cls)
        lp.name = row.name
        lp.publisher = row.publisher
        lp.isGlobal = row.is_global
        lp.version = row.version
        lp.summary = row.summary or ""
        lp.autoScan = False  # deprecated — always False
        lp.path = row.path
        lp.mode = row.mode if isinstance(row.mode, str) else "default"
        lp._supported_modes = row.mode if isinstance(row.mode, list) else ["source", "static"]
        lp.dependencies = [
            LibPackage.Dependency(d.get("name", ""), d.get("version", ""))
            for d in (row.dependencies or [])
        ]
        lp.success = True
        return lp

    @classmethod
    def query_all_from_db(cls):
        session = get_session()
        try:
            rows = session.query(LibPackageTable).all()
            return [cls.from_db_row(row) for row in rows]
        finally:
            session.close()

    def getDetail(self):
        from scripts.data.models import LibPackageDetailTable
        from scripts.data.models import get_session as _gs
        s = _gs()
        try:
            return s.query(LibPackageDetailTable).filter_by(
                group=self.publisher, name=self.name, version=self.version
            ).first()
        finally:
            s.close()

    @classmethod
    def _virtual_from_resolve(cls, path, name, publisher, version, resolve):
        lp = cls.__new__(cls)
        lp.name = name
        lp.publisher = publisher or "local"
        lp.version = version or "default"
        lp.path = os.path.normpath(path)
        lp.isGlobal = True
        lp.summary = f"[virtual] {lp.publisher}/{lp.name}"
        lp.mode = resolve.get("mode", "sources") if resolve else "sources"
        lp._supported_modes = resolve.get("mode", ["source", "static"]) if resolve else ["source", "static"]
        lp.dependencies = []
        lp.success = True
        lp.autoScan = False
        lp._virtual_resolve = resolve
        return lp

    def isMatch(self, package):
        """Match against either AppPackage (legacy) or RefPackage."""
        from scripts.data.RefPackage import RefPackage
        if isinstance(package, RefPackage):
            if "/" in package.name:
                matched = (self.publisher == package.name.split("/")[0]
                           and self.name == package.name.split("/")[1]
                           and package.version_range.contains(Version(self.version)))
            else:
                matched = (self.isGlobal and self.name == package.name
                           and package.version_range.contains(Version(self.version)))
            if not matched:
                return False
            user_mode = package.mode if package.mode != "default" else "source"
            return user_mode in getattr(self, "_supported_modes", ["source", "static"])
        if "/" in package.name:
            return (self.publisher == package.name.split("/")[0]
                    and self.name == package.name.split("/")[1]
                    and package.versionSpec.contains(Version(self.version)))
        return (self.isGlobal and self.name == package.name
                and package.versionSpec.contains(Version(self.version)))