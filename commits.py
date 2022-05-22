import subprocess

import path_utils


def get_commit_changed_files(folder: str) -> list[list[str]]:
    command = f"cd {folder} && git log --pretty=format:'' --name-only | cat"
    try:
        run_result = subprocess.run(
            command,
            shell=True, check=True, capture_output=True
        )
        output = run_result.stdout.decode("utf-8")
        commits = output.split("\n\n")
        return [
            [
                file.strip()
                for file in commit_files.split("\n")
                if file.strip() != ""
            ]
            for commit_files in commits
        ]
    except:
        return []


def get_changes_count(repo_path: str, java_files: list[str]) -> dict[tuple[str], list[int]]:
    base_tuple = path_utils.get_path_tuple(repo_path)

    module_changes = {
        path_utils.remove_prefix_tuple(
            base_tuple, path_utils.get_path_tuple(module_path)
        ): []
        for module_path in java_files
    }
    modules = list(module_changes.keys())

    commit_history = get_commit_changed_files(repo_path)

    for commit_files in commit_history:
        changed_modules = list(filter(
            lambda m: m is not None,
            map(
                lambda file: path_utils.find_closest_module(
                    path_utils.get_path_tuple(file),
                    modules
                ),
                commit_files
            )
        ))
        for m in changed_modules:
            module_changes[m].append(len(changed_modules))
    
    return module_changes
