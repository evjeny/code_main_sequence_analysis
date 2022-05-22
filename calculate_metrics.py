from dataclasses import dataclass
import glob
import os

from config_manager.config import Config

import commits
import variability


class MetricsConfig(Config):
    repos_folder: str
    output_json: str


@dataclass
class RepoMetrics:
    variability: float
    commit_count: list[int]


def is_repo(path: str) -> bool:
    return os.path.exists(
        os.path.join(path, ".git")
    )


def calculate_repo_metrics(
    folder: str,
    java_extensions: tuple[str] = (".java", )
) -> dict[tuple[str], RepoMetrics]:
    """
    Arguments:
        folder: str -> path to repo folder
    Returns:
        mapping [class_path, metrics] -> metrics for each class
    """

    java_files = list(filter(
        lambda name: any(name.endswith(ext) for ext in java_extensions),
        glob.glob(os.path.join(folder, "**"), recursive=True)
    ))

    variabilities = variability.get_variability(folder, java_files)
    changes_per_commit = commits.get_changes_count(folder, java_files)
    
    common_modules = set(variabilities.keys()).intersection(
        set(changes_per_commit.keys())
    )

    return {
        module: RepoMetrics(
            variability=variabilities[module],
            commit_count=changes_per_commit[module]
        )
        for module in common_modules
    }


def main(config: MetricsConfig):
    repos = list(filter(
        is_repo,
        map(
            lambda name: os.path.join(config.repos_folder, name),
            os.listdir(config.repos_folder)
        )
    ))

    print(f"{len(repos)} repositories")


if __name__ == "__main__":
    main(MetricsConfig().parse_arguments("Metrics calculator"))
