from dataclasses import dataclass
import glob
import os

from config_manager.config import Config

import variability


class MetricsConfig(Config):
    repos_folder: str
    output_json: str


@dataclass
class RepoMetrics:
    abstractness: float
    variability: float


def is_repo(path: str) -> bool:
    return os.path.exists(
        os.path.join(path, ".git")
    )


def calculate_repo_metrics(
    folder: str,
    java_extensions: tuple[str] = (".java", )
) -> dict[str, RepoMetrics]:
    """
    Arguments:
        folder: str -> path to repo folder
    Returns:
        mapping [class_path, metrics]
    """

    java_files = list(filter(
        lambda name: any(name.endswith(ext) for ext in java_extensions),
        glob.glob(os.path.join(folder, "**"), recursive=True)
    ))

    print(variability.get_variability(folder, java_files))


def main(config: MetricsConfig):
    repos = list(filter(
        is_repo,
        map(
            lambda name: os.path.join(config.repos_folder, name),
            os.listdir(config.repos_folder)
        )
    ))

    print(f"{len(repos)} repositories")

    repo_path = repos[2]
    print(repo_path)
    calculate_repo_metrics(repo_path)


if __name__ == "__main__":
    main(MetricsConfig().parse_arguments("Metrics calculator"))
