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
    
    def collect_refs(self, start_node: dict) -> set[str]:
        """
        Traverses the node and collects all $ref values recursively
        """
        queue = [start_node]
        result = set()

        while len(queue) > 0:
            node = queue.pop(0)
            refs = SpecFormatter._collect_refs_from_node(node)
            for ref in refs:
                if ref not in result:
                    result.add(ref)
                    ref_node = SpecFormatter.get_node(self, self._spec, ref[2:].split("/"))
                    queue.append(ref_node)
        return result
    
    def select_nodes(self, refs: set[str]) -> dict:
        """
        Selects nodes from the spec based on the refs. Preserves the structure of the spec.
        """
        result = {}
        for ref in refs:
            path = ref[2:].split("/")
            node = SpecFormatter.get_node(self, self._spec, path)
            result = SpecFormatter._merge_node(result, node, path)
        return result
    
    @staticmethod
    def _merge_node(result: dict, node: dict, path: list[str]) -> dict:
        if len(path) == 0:
            return node
        if path[0] not in result:
            result[path[0]] = {}
        result[path[0]] = SpecFormatter._merge_node(result[path[0]], node, path[1:])
        return result

    def _collect_refs_from_node(node: dict) -> list[str]:
        result = []
        if "$ref" in node:
            ref = node["$ref"]
            if ref.startswith("#/"):
                result.append(ref)
            else:
                raise NotImplementedError("External refs not supported yet")
        else:
            for key in node:
                if isinstance(node[key], dict):
                    refs = SpecFormatter._collect_refs_from_node(node[key])
                    result.extend(refs)
                elif isinstance(node[key], list):
                    for item in node[key]:
                        if isinstance(item, dict):
                            refs = SpecFormatter._collect_refs_from_node(item)
                            result.extend(refs)
        return result

    @staticmethod
    def get_node(self, node: dict, path: list[str]):
        if len(path) == 0:
            return node
        if path[0] not in node:
            raise KeyError(f"Path not found: {path}")
        return SpecFormatter.get_node(self, node[path[0]], path[1:])

    @staticmethod
    def _trim_path(path_obj):
        return {
            method: SpecFormatter._trim_method(path_obj[method]) for method in path_obj
        }

    @staticmethod
    def _trim_method(method_obj):
        obj = {}
        for key in ["summary", "description", "parameters", "requestBody"]:
            if key not in method_obj:
                continue
            obj[key] = method_obj[key]
        return obj
