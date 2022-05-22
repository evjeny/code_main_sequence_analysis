import variability


def test_get_imports():
    target_imports = ["java.lang.String", "java.utils.*", "com.evjeny.prod.*"]
    content = "\n".join(f"import {target};" for target in target_imports) + "\n\nclass Hello {}"

    found_imports = variability.get_imports(content)
    assert all(target in found_imports for target in target_imports)


def test_get_import_tuple():
    assert variability.get_import_tuple("hello.world.JarCreator") == ("hello", "world", "JarCreator.java")
    assert variability.get_import_tuple("java.utils.*") == ("java", "utils", "*.java")
