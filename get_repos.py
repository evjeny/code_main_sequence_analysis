import itertools
import json
from multiprocessing import Pool
import subprocess

from config_manager.config import Config


class ScraperConfig(Config):
    url_json_path: str
    target_folder: str
    n_workers: int = 5


def get_repo_urls(json_path: str) -> list[str]:
    with open(json_path) as f:
        return [
            r["url"] for r in json.load(f)
        ]


def clone_repo(url: str, base_folder: str) -> bool:
    command = f"cd {base_folder} && gh repo clone {url}"
    try:
        subprocess.run(command, shell=True, check=True)
        return True
    except:
        return False


def main(config: ScraperConfig):
    urls = get_repo_urls(config.url_json_path)

    with Pool(config.n_workers) as pool:
        result_mask = pool.starmap(
            clone_repo,
            zip(
                urls,
                itertools.repeat(config.target_folder, len(urls))
            )
        )

    n_success = len([1 for success in result_mask if success])
    print(f"Cloned {n_success}/{len(urls)} repos")


if __name__ == "__main__":
    main(ScraperConfig().parse_arguments("Scrap Github repos"))
