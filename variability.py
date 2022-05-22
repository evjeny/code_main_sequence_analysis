import itertools
import os
import re
from typing import Optional


def read_file(path: str) -> str:
    with open(path) as f:
        return f.read()


def get_imports(file_content: str) -> list[str]:
    return re.findall(r"(?<=import )[^\s]*(?=;)", file_content)


def get_path_tuple(path: str) -> tuple[str]:
    return tuple(os.path.normpath(path).split(os.sep))


def remove_prefix_tuple(prefix: tuple[str], target: tuple[str]) -> tuple[str]:
    i = 0
    while i < min(len(prefix), len(target)) and prefix[i] == target[i]:
        i += 1
    return target[i:]


def get_import_tuple(import_str: str) -> tuple[str]:
    parts = import_str.split(".")
    return tuple(parts[:-1] + [parts[-1] + ".java"])


def count_similar_endings(
    tuple_a: tuple[str],
    tuple_b: tuple[str]
) -> int:
    index_a = len(tuple_a) - 1
    index_b = len(tuple_b) - 1
    count = 0

    while index_a >= 0 and index_b >= 0 and tuple_a[index_a] == tuple_b[index_b]:
        index_a -= 1
        index_b -= 1
        count += 1

    return count


def find_closest_module(
    target_module: tuple[str],
    modules: list[tuple[str]]
) -> Optional[tuple[str]]:
    max_endings = 0
    probable_module = None

    for m in modules:
        cur_endings = count_similar_endings(target_module, m)
        if cur_endings > max_endings:
            max_endings = cur_endings
            probable_module = m
    
    return probable_module


def get_variability_score(depends_on: int, dependency_for: int) -> float:
    return depends_on / max(dependency_for + depends_on, 1)


def get_variability(repo_path: str, java_files: list[str]) -> dict[tuple[str], float]:
    base_tuple = get_path_tuple(repo_path)

    module_imports = {
        remove_prefix_tuple(
            base_tuple, get_path_tuple(module_path)
        ): list(map(get_import_tuple, get_imports(read_file(module_path))))
        for module_path in java_files
    }

    modules = list(module_imports.keys())

    module_stats = {
        module_tuple: {"depends_on": len(dep_tuples), "dependency_for": 0}
        for module_tuple, dep_tuples in module_imports.items()
    }

    for dep_tuple in itertools.chain(*module_imports.values()):
        probable_module = find_closest_module(dep_tuple, modules)
        if probable_module:
            module_stats[probable_module]["dependency_for"] += 1
    
    return {
        module: get_variability_score(stats["depends_on"], stats["dependency_for"])
        for module, stats in module_stats.items()
    }
