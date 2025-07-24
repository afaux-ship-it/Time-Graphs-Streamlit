"""Box-plot builder."""
from __future__ import annotations

from typing import Dict, List, Optional

import pandas as pd
import plotly.graph_objects as go

from .base import BasePlotter

__all__ = ["create_box_plot"]


def create_box_plot(
    df: pd.DataFrame,
    x_column: str,
    y_columns: List[str],
    config: Optional[Dict] = None,
) -> go.Figure:
    bp = BasePlotter()
    cfg = {**bp.default_config, **(config or {})}

    # Prepare grouping on copy to avoid mutating original
    dfc = df.copy()

    if pd.api.types.is_datetime64_any_dtype(dfc[x_column]):
        span = dfc[x_column].max() - dfc[x_column].min()
        if span.days > 730:
            dfc["time_group"] = dfc[x_column].dt.to_period("Y").astype(str)
        elif span.days > 60:
            dfc["time_group"] = dfc[x_column].dt.to_period("M").astype(str)
        else:
            dfc["time_group"] = dfc[x_column].dt.to_period("D").astype(str)
    else:
        dfc["time_group"] = pd.cut(dfc[x_column], bins=10).astype(str)

    fig = go.Figure()
    colors = bp._get_colors(len(y_columns), cfg.get("color_palette", "Default"))  # noqa: SLF001

    for i, col in enumerate(y_columns):
        for grp in dfc["time_group"].unique():
            subset = dfc[dfc["time_group"] == grp][col].dropna()
            if not subset.empty:
                fig.add_trace(
                    go.Box(
                        y=subset,
                        x=[grp] * len(subset),
                        name=f"{col} - {grp}",
                        marker_color=colors[i % len(colors)],
                        showlegend=(i == 0),
                    )
                )

    bp._apply_layout(fig, cfg, "Time Groups", y_columns)  # noqa: SLF001
    return fig
