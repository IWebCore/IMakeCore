import json
from packaging.specifiers import *
from packaging.version import *

class Utils:

    @staticmethod
    def loadJson( path):
        with open(path, "rt", encoding="utf-8") as f:   # anoying utf-8 BOM!!!!
            try:
                content = f.read()
                if content.startswith('\ufeff'):
                    content = content[1:]
                value = json.loads(content)
                return value
            except json.JSONDecodeError as e:
                error_info = f"type: {type(e).__name__}\nmessage: {e.msg}\nLine: {e.lineno} Column: {e.colno} File: {path}"
                print("package.json error: " + error_info)
                exit(1)

    @staticmethod
    def parseVersionSpecifier(version:str):
        if not version.strip():
            return SpecifierSet(">=0")
        
        if version == "*":
            return SpecifierSet(">=0")
        
        try:
            Version(version)
            return SpecifierSet(f"=={version}")
        except InvalidVersion:
            try:
                return SpecifierSet(version) 
            except InvalidSpecifier as e:
                print(f"error: {e}\n'{version}' is not a valid version specifier")
                exit(1)