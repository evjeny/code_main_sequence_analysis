from dataclasses import dataclass
import itertools
import re

import path_utils


@dataclass
class Dependencies:
    depends_on: int
    dependency_for: int
    score: float


def read_file(path: str) -> str:
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except:
        return ""


def get_imports(file_content: str) -> list[str]:
    return re.findall(r"(?<=import )[^\s]*(?=;)", file_content)


def get_import_tuple(import_str: str) -> tuple[str]:
    parts = import_str.split(".")
    return tuple(parts[:-1] + [parts[-1] + ".java"])


def get_variability_score(depends_on: int, dependency_for: int) -> float:
    return depends_on / max(dependency_for + depends_on, 1)


def get_variability(repo_path: str, java_files: list[str]) -> dict[tuple[str], Dependencies]:
    base_tuple = path_utils.get_path_tuple(repo_path)

    module_imports = {
        path_utils.remove_prefix_tuple(
            base_tuple, path_utils.get_path_tuple(module_path)
        ): list(map(get_import_tuple, get_imports(read_file(module_path))))
        for module_path in java_files
    }

    modules = list(module_imports.keys())

    module_stats = {
        module_tuple: {"depends_on": len(dep_tuples), "dependency_for": 0}
        for module_tuple, dep_tuples in module_imports.items()
    }

    for dep_tuple in itertools.chain(*module_imports.values()):
        probable_module = path_utils.find_closest_module(dep_tuple, modules)
        if probable_module:
            module_stats[probable_module]["dependency_for"] += 1
    
    return {
        module: Dependencies(
            depends_on=stats["depends_on"],
            dependency_for=stats["dependency_for"],
            score=get_variability_score(stats["depends_on"], stats["dependency_for"])
        )
        for module, stats in module_stats.items()
    }
