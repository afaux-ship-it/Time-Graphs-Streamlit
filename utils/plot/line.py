"""Line-chart builder."""
from __future__ import annotations

from typing import Dict, List, Optional

import pandas as pd
import plotly.graph_objects as go

from .base import BasePlotter

__all__ = ["create_line_chart"]


def create_line_chart(
    df: pd.DataFrame,
    x_column: str,
    y_columns: List[str],
    config: Optional[Dict] = None,
) -> go.Figure:
    """Return a Plotly Figure representing a time-series line chart."""
    bp = BasePlotter()
    cfg = {**bp.default_config, **(config or {})}

    fig = go.Figure()
    colors = bp._get_colors(len(y_columns), cfg.get("color_palette", "Default"))  # noqa: SLF001

    for i, col in enumerate(y_columns):
        fig.add_trace(
            go.Scatter(
                x=df[x_column],
                y=df[col],
                mode="lines+markers" if cfg.get("show_markers", True) else "lines",
                name=col,
                line=dict(width=cfg.get("line_width", 2), color=colors[i % len(colors)]),
                marker=dict(size=cfg.get("marker_size", 6), opacity=cfg.get("opacity", 0.8)),
                opacity=cfg.get("opacity", 0.8),
            )
        )

    bp._apply_layout(fig, cfg, x_column, y_columns)  # noqa: SLF001
    return fig
