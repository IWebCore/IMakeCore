"""
FileFilter.py — Gitignore-style file exclusion using Strategy pattern.
Easily extensible with additional filter rules (e.g., size-based, date-based).
"""
import os
import pathspec


class FilterRule:
    def apply(self, files, root_paths):
        raise NotImplementedError


class GitignoreRule(FilterRule):
    def __init__(self, patterns):
        self.patterns = patterns if isinstance(patterns, list) else [patterns]

    def apply(self, files, root_paths):
        if not self.patterns or not files:
            return files
        specs = {}
        for root in root_paths:
            specs[root] = pathspec.PathSpec.from_lines("gitwildmatch", self.patterns)
        result = []
        for f in files:
            owner = None
            for root in root_paths:
                try:
                    rel = os.path.relpath(f, root)
                    if not rel.startswith(".."):
                        owner = root
                        break
                except ValueError:
                    continue
            if owner is None:
                result.append(f)
                continue
            rel_path = os.path.relpath(f, owner).replace(os.sep, "/")
            if not specs[owner].match_file(rel_path):
                result.append(f)
        return result


class FileFilter:
    def __init__(self):
        self.rules = []

    def add_rule(self, rule):
        self.rules.append(rule)

    def remove_rule(self, rule):
        self.rules.remove(rule)

    def apply(self, files, root_paths):
        result = files
        for rule in self.rules:
            result = rule.apply(result, root_paths)
        return result
