import json
from typing import Union

from config_manager.config import Config
import numpy as np
from matplotlib.axes import Axes
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


params_t = dict[str, Union[int, list[int]]]
modules_t = dict[str, params_t]
project_t = dict[str, modules_t]


class PlotConfig(Config):
    metrics_path: str
    output_fig: str = "show" # filename or "show"
    fig_width: int = 16
    fig_height: int = 12


def plot_variability_to_files(
    metrics: project_t,
    ax: Axes
):
    def variability_to_category(variability: float) -> str:
        thresholds = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
        for r_begin, r_end in zip(thresholds[:-1], thresholds[1:]):
            if r_begin <= variability <= r_end:
                return f"{r_begin:.1f}-{r_end:.1f}"
        return "???"

    variability_n_files: list[tuple[float, int]] = [
        (params["dependency_score"], count)
        for modules in metrics.values()
        for params in modules.values()
        for count in params["commit_count"]
    ]
    dots = np.array(variability_n_files)

    data = pd.DataFrame({
        "variability": dots[:, 0],
        "#files_changed": dots[:, 1]
    })
    data["var_cat"] = data["variability"].apply(variability_to_category)

    var_cats = sorted(data["var_cat"].unique().tolist())

    ax.set_title("Variability to # changed files")
    sns.boxplot(
        x="var_cat",
        y="#files_changed",
        data=data,
        order=var_cats,
        showfliers=False,
        ax=ax
    )


def plot_project_size_to_files(
    metrics: project_t,
    ax: Axes
):
    def module_commit_counts_to_mean(param_list: list[params_t]) -> float:
        if len(param_list) == 0:
            return 0.0
        
        return np.mean(np.nan_to_num(
            [
                np.median(params["commit_count"] if len(params["commit_count"]) else [1])
                for params in param_list
            ]
        ))

    size_files: list[tuple[int, int]] = [
        (
            len(modules),
            module_commit_counts_to_mean(list(modules.values()))
        )
        for modules in metrics.values()
    ]

    dots = np.array(size_files)

    data = pd.DataFrame({
        "#modules": dots[:, 0],
        "#mean_of_meadian_files_changed": dots[:, 1]
    })
    # filter too big projects for visualization
    data = data[data["#modules"] <= 2000]

    ax.set_title("# modules to # changed files")
    sns.regplot(
        x="#modules",
        y="#mean_of_meadian_files_changed",
        data=data,
        scatter_kws={"alpha": 0.1, "color": "blue"},
        line_kws={"color": "red"},
        ax=ax
    )


def plot_dependencies_to_files(
    metrics: project_t,
    ax_depends_on: Axes,
    ax_dependency_for: Axes
):
    deps_n_files: list[tuple[float, int]] = [
        (params["depends_on"], params["dependency_for"], count)
        for modules in metrics.values()
        for params in modules.values()
        for count in params["commit_count"]
    ]
    dots = np.array(deps_n_files)

    data = pd.DataFrame({
        "depends_on": dots[:, 0],
        "dependency_for": dots[:, 1],
        "#files_changed": dots[:, 2]
    })

    ax_depends_on.set_title("# used imports to # changed files")
    sns.regplot(
        x="depends_on",
        y="#files_changed",
        data=data,
        scatter_kws={"alpha": 0.1, "color": "red"},
        line_kws={"color": "blue"},
        ax=ax_depends_on
    )

    ax_dependency_for.set_title("# used as import to # changed files")
    sns.regplot(
        x="dependency_for",
        y="#files_changed",
        data=data,
        scatter_kws={"alpha": 0.1, "color": "green"},
        line_kws={"color": "blue"},
        ax=ax_dependency_for
    )


def main(config: PlotConfig):
    with open(config.metrics_path, "rb") as f:
        metrics: project_t = json.load(f)

    _, (
        (ax_var_files, ax_psize_files),
        (ax_don_files, ax_dfor_files)
    ) = plt.subplots(2, 2, figsize=(config.fig_width, config.fig_height))
    
    plot_variability_to_files(metrics, ax_var_files)
    plot_project_size_to_files(metrics, ax_psize_files)
    plot_dependencies_to_files(metrics, ax_don_files, ax_dfor_files)

    if config.output_fig == "show":
        plt.show()
    else:
        plt.savefig(config.output_fig)


if __name__ == "__main__":
    main(PlotConfig().parse_arguments("Plot metrics"))
