from typing import Optional
from .types import ApiEndpoint
from collections import defaultdict


class SpecFormatter:
    _spec: Optional[dict] = None

    def __init__(self, spec: dict):
        self._spec = spec

    def trim_paths_only(self) -> Optional[dict]:
        if not self._spec or "paths" not in self._spec:
            return None
        paths = self._spec["paths"]
        trimmed_paths = {path: SpecFormatter._trim_path(paths[path]) for path in paths}
        return {
            "paths": trimmed_paths,
        }

    def narrow_api_list(self, apis: list[ApiEndpoint]) -> Optional[dict]:
        if not self._spec or "paths" not in self._spec:
            return None

        apimap = defaultdict(defaultdict)
        for api in apis:
            apimap[api.path][api.verb.lower()] = True

        paths = {}
        for path in self._spec["paths"]:
            if path not in apimap:
                continue
            paths[path] = {}
            for verb in self._spec["paths"][path]:
                if verb not in apimap[path]:
                    continue
                paths[path][verb] = self._spec["paths"][path][verb]

        trimmed_paths = {path: SpecFormatter._trim_path(paths[path]) for path in paths}
        return {
            "paths": trimmed_paths,
        }

    @staticmethod
    def _trim_path(path_obj):
        return {
            method: SpecFormatter._trim_method(path_obj[method]) for method in path_obj
        }

    @staticmethod
    def _trim_method(method_obj):
        obj = {}
        for key in ["summary", "description", "parameters"]:
            if key not in method_obj:
                continue
            obj[key] = method_obj[key]
        return obj
