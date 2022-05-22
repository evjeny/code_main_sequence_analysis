from dataclasses import dataclass
import glob
import json
from multiprocessing import Pool, cpu_count
import os

from config_manager.config import Config

import commits
import variability


class MetricsConfig(Config):
    repos_folder: str
    output_json: str


@dataclass
class RepoMetrics:
    variability: variability.Dependencies
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


def dump_metrics(path: str, repo_data: dict[str, dict[tuple[str], RepoMetrics]]):
    with open(path, "w+") as f:
        decoded = {
            repo_name: [
                {
                    "/".join(module): {
                        "depends_on": metrics.variability.depends_on,
                        "dependency_for": metrics.variability.dependency_for,
                        "dependency_score": metrics.variability.score,
                        "commit_count": metrics.commit_count
                    }
                }
                for module, metrics in repo_metrics.items()
            ]
            for repo_name, repo_metrics in repo_data.items()
        }
        f.write(json.dumps(decoded))


def main(config: MetricsConfig):
    repos = list(filter(
        is_repo,
        map(
            lambda name: os.path.join(config.repos_folder, name),
            os.listdir(config.repos_folder)
        )
    ))

    print(f"{len(repos)} repositories")

    repo_data = dict()
    with Pool(cpu_count()) as pool:
        for repo_path, metrics in zip(repos, pool.map(calculate_repo_metrics, repos)):
            repo_data[repo_path.removeprefix(config.repos_folder)] = metrics

    dump_metrics(config.output_json, repo_data)


if __name__ == "__main__":
    main(MetricsConfig().parse_arguments("Metrics calculator"))
