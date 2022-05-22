import os

import variability


def test_get_imports():
    target_imports = ["java.lang.String", "java.utils.*", "com.evjeny.prod.*"]
    content = "\n".join(f"import {target};" for target in target_imports) + "\n\nclass Hello {}"

    found_imports = variability.get_imports(content)
    assert all(target in found_imports for target in target_imports)


def test_get_path_tuple():
    for parts in [("hello", ), ("really", "hello", "world", "2.exe")]:
        assert variability.get_path_tuple(os.path.join(*parts)) == parts


def test_remove_prefix_tuple():
    target_tuple = ("one", "more", "file.txt")
    for prefix in [(), ("hello", ), ("hello", "world")]:
        assert variability.remove_prefix_tuple(prefix, target_tuple) == target_tuple
        assert variability.remove_prefix_tuple(prefix, prefix + target_tuple) == target_tuple


def test_get_import_tuple():
    assert variability.get_import_tuple("hello.world.JarCreator") == ("hello", "world", "JarCreator.java")
    assert variability.get_import_tuple("java.utils.*") == ("java", "utils", "*.java")


def test_count_similar_endings():
    for base_tuple in [("a",), ("a", "b"), ("a", "b", "c")]:
        assert variability.count_similar_endings(base_tuple, ("1", "a") + base_tuple) == len(base_tuple)
        assert variability.count_similar_endings(base_tuple, base_tuple + ("1", "2")) == 0


def test_import_to_module():
    modules = [("a", "b", "c"), ("a", "b", "d"), ("t", "q"), ("f", )]
    for m in modules:
        assert variability.find_closest_module(m, modules) == m
        assert variability.find_closest_module(("src", "main") + m, modules) == m
    
    assert variability.find_closest_module(("hello", "world"), modules) is None
