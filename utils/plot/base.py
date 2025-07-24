"""Base plotting helpers extracted from the monolithic `plot_generator.py`.

A thin `BasePlotter` class centralises colour handling, layout defaults,
trend-line helpers, transparency tweaks and figure export.  Concrete chart
builders (e.g. line, scatter) can now inherit from this class or simply call
its static helpers.
"""
from __future__ import annotations

from typing import Dict, List

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots  # noqa: F401 – may be useful for builders

import config

__all__ = [
    "BasePlotter",
]


class BasePlotter:  # pylint: disable=too-few-public-methods
    """Common utilities for all plot builders."""

    COLOR_PALETTES = config.COLOR_PALETTES  # type: ignore[attr-defined]

    def __init__(self, default_cfg: Dict | None = None):
        # copy() to avoid mutating global dict
        self.default_config: Dict = {
            **config.DEFAULT_PLOT_CONFIG,  # type: ignore[attr-defined]
            **(default_cfg or {}),
        }

    # ---------------------------------------------------------------------
    # Colour and style helpers
    # ---------------------------------------------------------------------
    @classmethod
    def _get_colors(cls, n_colors: int, palette_name: str = "Default") -> List[str]:
        """Return *n_colors* hex strings from the chosen palette."""
        if palette_name in cls.COLOR_PALETTES:
            colors = cls.COLOR_PALETTES[palette_name]
            return (colors * ((n_colors // len(colors)) + 1))[:n_colors]
        return px.colors.qualitative.Plotly[:n_colors]

    @staticmethod
    def _add_transparency(color: str, alpha: float) -> str:
        """Convert a hex colour to an rgba string with *alpha* transparency."""
        if color.startswith("#") and len(color) == 7:
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)
            return f"rgba({r},{g},{b},{alpha})"
        return color  # already rgba or named

    # ------------------------------------------------------------------
    # Figure-level helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _apply_layout(fig: go.Figure, cfg: Dict, x_label: str, y_columns: List[str]):
        """Apply titles, theme and axis tweaks to *fig* using *cfg*."""
        fig.update_layout(
            title=cfg.get("title", f"{', '.join(y_columns)} vs {x_label}"),
            xaxis_title=cfg.get("x_title", x_label),
            yaxis_title=cfg.get("y_title", ", ".join(y_columns)),
            width=cfg.get("width", 800),
            height=cfg.get("height", 500),
            template=cfg.get("theme", "plotly_white"),
            font=dict(size=cfg.get("font_size", 12)),
            hovermode="x unified" if cfg.get("unified_hover", True) else "closest",
            legend=dict(
                orientation=cfg.get("legend_orientation", "v"),
                yanchor=cfg.get("legend_yanchor", "top"),
                y=cfg.get("legend_y", 1),
                xanchor=cfg.get("legend_xanchor", "left"),
                x=cfg.get("legend_x", 1.02),
            ),
        )

        # axis options
        if cfg.get("x_range") is not None:
            fig.update_xaxes(range=cfg["x_range"])
        if cfg.get("y_range") is not None:
            fig.update_yaxes(range=cfg["y_range"])
        if cfg.get("log_y", False):
            fig.update_yaxes(type="log")
        if cfg.get("log_x", False):
            fig.update_xaxes(type="log")
        if cfg.get("show_grid", True):
            fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor="lightgray")
            fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor="lightgray")

    # ------------------------------------------------------------------
    # Statistical helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _add_trendline(fig: go.Figure, x_data: pd.Series, y_data: pd.Series, color: str):
        """Add a simple first-order poly trend line to *fig*.  Silently skips on errors."""
        try:
            x_numeric = (
                pd.to_numeric(x_data) if pd.api.types.is_datetime64_any_dtype(x_data) else x_data
            )
            mask = ~(pd.isna(x_numeric) | pd.isna(y_data))
            x_clean = x_numeric[mask]
            y_clean = y_data[mask]
            if len(x_clean) > 1:
                z = np.polyfit(x_clean, y_clean, 1)
                p = np.poly1d(z)
                fig.add_trace(
                    go.Scatter(
                        x=x_data,
                        y=p(x_numeric),
                        mode="lines",
                        name="Trend",
                        line=dict(dash="dash", color=color, width=1),
                        opacity=0.7,
                    )
                )
        except Exception:  # pylint: disable=broad-except
            pass

    # ------------------------------------------------------------------
    # Export helpers
    # ------------------------------------------------------------------
    @staticmethod
    def export_plot(
        fig: go.Figure,
        format_: str = "png",
        width: int = 800,
        height: int = 500,
        scale: int = 2,
    ) -> bytes:
        """Return the raw bytes for *fig* in the requested format."""
        if format_.lower() == "html":
            return fig.to_html(include_plotlyjs=True).encode()
        if format_.lower() in {"png", "jpeg", "svg", "pdf"}:
            return fig.to_image(format=format_.lower(), width=width, height=height, scale=scale)
        raise ValueError(f"Unsupported export format: {format_}")
