import os
from scripts.data.models import get_session
from scripts.data.models import LibPackageDetailTable


class MakePackageGenerator:

    @staticmethod
    def _normalize_path(p):
        return os.path.normpath(p).replace(os.sep, "/")

    @staticmethod
    def _get_detail_from_db(publisher, name, version):
        session = get_session()
        try:
            return session.query(LibPackageDetailTable).filter_by(
                group=publisher, name=name, version=version
            ).first()
        finally:
            session.close()

    @staticmethod
    def _get_file_paths(detail):
        if detail is None:
            return None
        return {
            "headers": detail.get_headers(),
            "sources": detail.get_sources(),
            "uis": detail.get_uis(),
            "resources": detail.get_resources(),
            "definitions": detail.get_definitions(),
            "includes": detail.get_includes(),
            "precompile_headers": detail.get_precompile_headers(),
        }

    @staticmethod
    def _lib_output_path(lp, env, suffix):
        name = f"{lp.publisher}@{lp.name}@{lp.version}.{suffix}"
        return os.path.join(env.appLibStore, name)

    @staticmethod
    def _write_if_changed(path, content):
        if os.path.exists(path):
            with open(path, "rt", encoding="utf-8") as f:
                if f.read() == content:
                    return path
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wt", encoding="utf-8") as f:
            f.write(content)
        return path

    @staticmethod
    def _header_comment(lp):
        return [
            "# SYSTEM AUTO GENERATED DO NOT EDIT!!!",
            f"# {lp.publisher}@{lp.name}@{lp.version}",
            f"# {lp.summary or ''}",
            "",
        ]

    def generate(self, pkg, env):
        raise NotImplementedError

    def post_process(self, packages, env):
        raise NotImplementedError
