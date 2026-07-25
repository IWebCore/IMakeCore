class LibName:
    def __init__(self, name: str = "", publisher: str = "", is_global: bool = True):
        if "/" in name:
            parts = name.split("/", 1)
            self.publisher = parts[0].strip()
            self.name = parts[1].strip()
            self.is_global = False
        else:
            self.name = name.strip()
            self.publisher = publisher
            self.is_global = is_global

    @staticmethod
    def fromRaw(name : str):
        if "/" in name:
            args = name.split("/")
            return LibName(args[1], args[0])
        else:
            return LibName(name)
        

    def isValid(self) -> bool:
        if not self.name:
            return False
        if not self.publisher and not self.is_global:
            return False
        return True

    def fullName(self, spliter: str = "/") -> str:
        return f"{self.publisher}{spliter}{self.name}" if self.publisher else self.name

    def __eq__(self, other) -> bool:
        if isinstance(other, LibName):
            return self.fullName() == other.fullName()
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self.fullName())

    def __repr__(self) -> str:
        return f"<LibName {self.fullName()}>"
