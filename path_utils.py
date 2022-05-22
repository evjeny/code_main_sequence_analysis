import os
from typing import Optional


def get_path_tuple(path: str) -> tuple[str]:
    return tuple(os.path.normpath(path).split(os.sep))


def remove_prefix_tuple(prefix: tuple[str], target: tuple[str]) -> tuple[str]:
    i = 0
    while i < min(len(prefix), len(target)) and prefix[i] == target[i]:
        i += 1
    return target[i:]


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
