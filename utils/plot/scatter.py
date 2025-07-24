"""Scatter-plot builder."""
from __future__ import annotations

from typing import Dict, List, Optional

import pandas as pd
import plotly.graph_objects as go

from .base import BasePlotter

__all__ = ["create_scatter_plot"]


def create_scatter_plot(
    df: pd.DataFrame,
    x_column: str,
    y_columns: List[str],
    config: Optional[Dict] = None,
) -> go.Figure:
    """Return a scatter Plotly Figure."""
    bp = BasePlotter()
    cfg = {**bp.default_config, **(config or {})}

    fig = go.Figure()
    colors = bp._get_colors(len(y_columns), cfg.get("color_palette", "Default"))  # noqa: SLF001

    for i, col in enumerate(y_columns):
        fig.add_trace(
            go.Scatter(
                x=df[x_column],
                y=df[col],
                mode="markers",
                name=col,
                marker=dict(
                    size=cfg.get("marker_size", 8),
                    color=colors[i % len(colors)],
                    opacity=cfg.get("opacity", 0.7),
                    line=dict(width=1, color="white"),
                ),
            )
        )
        if cfg.get("show_trendline", False):
            bp._add_trendline(fig, df[x_column], df[col], colors[i % len(colors)])  # noqa: SLF001

    bp._apply_layout(fig, cfg, x_column, y_columns)  # noqa: SLF001
    return fig
