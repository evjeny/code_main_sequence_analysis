import os

import path_utils


def test_get_path_tuple():
    for parts in [("hello", ), ("really", "hello", "world", "2.exe")]:
        assert path_utils.get_path_tuple(os.path.join(*parts)) == parts


def test_remove_prefix_tuple():
    target_tuple = ("one", "more", "file.txt")
    for prefix in [(), ("hello", ), ("hello", "world")]:
        assert path_utils.remove_prefix_tuple(prefix, target_tuple) == target_tuple
        assert path_utils.remove_prefix_tuple(prefix, prefix + target_tuple) == target_tuple


def test_count_similar_endings():
    for base_tuple in [("a",), ("a", "b"), ("a", "b", "c")]:
        assert path_utils.count_similar_endings(base_tuple, ("1", "a") + base_tuple) == len(base_tuple)
        assert path_utils.count_similar_endings(base_tuple, base_tuple + ("1", "2")) == 0


def test_find_closest_module():
    modules = [("a", "b", "c"), ("a", "b", "d"), ("t", "q"), ("f", )]
    for m in modules:
        assert path_utils.find_closest_module(m, modules) == m
        assert path_utils.find_closest_module(("src", "main") + m, modules) == m
    
    assert path_utils.find_closest_module(("hello", "world"), modules) is None
