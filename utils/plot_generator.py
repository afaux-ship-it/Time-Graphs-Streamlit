"""
Plot generation utilities for Graph Anything Over Time application.
Handles creation of various chart types using Plotly, Matplotlib, and Seaborn.
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import config
import streamlit as st
from typing import Dict, List, Optional, Tuple, Any, Union
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')


class PlotGenerator:
    """Handles generation of various types of time-series plots."""
    
    # Color palettes
    COLOR_PALETTES = config.COLOR_PALETTES  # type: ignore
    # Color palettes centralized in config.py

    def __init__(self):
        """Initialize PlotGenerator."""
        self.default_config = config.DEFAULT_PLOT_CONFIG.copy()

    
    def create_line_chart(self, df: pd.DataFrame, 
                         x_column: str, 
                         y_columns: List[str],
                         config: Optional[Dict] = None) -> go.Figure:
        """
        Create a line chart.
        
        Args:
            df: DataFrame containing the data
            x_column: Name of the time/x-axis column
            y_columns: List of column names for y-axis
            config: Configuration dictionary

        Returns:
            Plotly Figure object
        """
        config = {**self.default_config, **(config or {})}
        
        fig = go.Figure()
        
        colors = self._get_colors(len(y_columns), config.get('color_palette', 'Default'))
        
        for i, col in enumerate(y_columns):
            fig.add_trace(go.Scatter(
                x=df[x_column],
                y=df[col],
                mode='lines+markers' if config.get('show_markers', True) else 'lines',
                name=col,
                line=dict(
                    width=config.get('line_width', 2),
                    color=colors[i % len(colors)]
                ),
                marker=dict(
                    size=config.get('marker_size', 6),
                    opacity=config.get('opacity', 0.8)
                ),
                opacity=config.get('opacity', 0.8)
            ))
        
        self._apply_layout(fig, config, x_column, y_columns)
        return fig
    
    def create_scatter_plot(self, df: pd.DataFrame,
                           x_column: str,
                           y_columns: List[str],
                           config: Optional[Dict] = None) -> go.Figure:
        """Create a scatter plot."""
        config = {**self.default_config, **(config or {})}
        
        fig = go.Figure()
        
        colors = self._get_colors(len(y_columns), config.get('color_palette', 'Default'))
        
        for i, col in enumerate(y_columns):
            fig.add_trace(go.Scatter(
                x=df[x_column],
                y=df[col],
                mode='markers',
                name=col,
                marker=dict(
                    size=config.get('marker_size', 8),
                    color=colors[i % len(colors)],
                    opacity=config.get('opacity', 0.7),
                    line=dict(width=1, color='white')
                )
            ))

            # Add trendline if requested
            if config.get('show_trendline', False):
                self._add_trendline(fig, df[x_column], df[col], colors[i % len(colors)])
        
        self._apply_layout(fig, config, x_column, y_columns)
        return fig
    
    def create_bar_chart(self, df: pd.DataFrame,
                        x_column: str,
                        y_columns: List[str],
                        config: Optional[Dict] = None) -> go.Figure:
        """Create a bar chart."""
        config = {**self.default_config, **(config or {})}
        
        fig = go.Figure()
        
        colors = self._get_colors(len(y_columns), config.get('color_palette', 'Default'))
        
        for i, col in enumerate(y_columns):
            fig.add_trace(go.Bar(
                x=df[x_column],
                y=df[col],
                name=col,
                marker_color=colors[i % len(colors)],
                opacity=config.get('opacity', 0.8)
            ))
        
        self._apply_layout(fig, config, x_column, y_columns)
        return fig
    
    def create_area_chart(self, df: pd.DataFrame,
                         x_column: str,
                         y_columns: List[str],
                         config: Optional[Dict] = None) -> go.Figure:
        """Create an area chart."""
        config = {**self.default_config, **(config or {})}
        
        fig = go.Figure()
        
        colors = self._get_colors(len(y_columns), config.get('color_palette', 'Default'))
        
        for i, col in enumerate(y_columns):
            fig.add_trace(go.Scatter(
                x=df[x_column],
                y=df[col],
                mode='lines',
                name=col,
                fill='tonexty' if i > 0 else 'tozeroy',
                line=dict(
                    width=config.get('line_width', 1),
                    color=colors[i % len(colors)]
                ),
                fillcolor=self._add_transparency(colors[i % len(colors)], 0.3)
            ))
        
        self._apply_layout(fig, config, x_column, y_columns)
        return fig
    
    def create_box_plot(self, df: pd.DataFrame,
                       x_column: str,
                       y_columns: List[str],
                       config: Optional[Dict] = None) -> go.Figure:
        """Create box plots grouped by time periods."""
        config = {**self.default_config, **(config or {})}
        
        # Group data by time periods (e.g., by month, year)
        df_copy = df.copy()
        
        # Determine grouping based on data span
        if pd.api.types.is_datetime64_any_dtype(df_copy[x_column]):
            date_range = df_copy[x_column].max() - df_copy[x_column].min()

            if date_range.days > 730:  # More than 2 years
                df_copy['time_group'] = df_copy[x_column].dt.to_period('Y').astype(str)
            elif date_range.days > 60:  # More than 2 months
                df_copy['time_group'] = df_copy[x_column].dt.to_period('M').astype(str)
            else:
                df_copy['time_group'] = df_copy[x_column].dt.to_period('D').astype(str)
        else:
            # For non-datetime x-axis, create bins
            df_copy['time_group'] = pd.cut(df_copy[x_column], bins=10).astype(str)
        
        fig = go.Figure()
        
        colors = self._get_colors(len(y_columns), config.get('color_palette', 'Default'))
        
        for i, col in enumerate(y_columns):
            for group in df_copy['time_group'].unique():
                group_data = df_copy[df_copy['time_group'] == group][col].dropna()
    
                if len(group_data) > 0:
                    fig.add_trace(go.Box(
                        y=group_data,
                        x=[group] * len(group_data),
                        name=f"{col} - {group}",
                        marker_color=colors[i % len(colors)],
                        showlegend=(i == 0)
                    ))
        
        self._apply_layout(fig, config, 'Time Groups', y_columns)
        return fig
    
    def create_candlestick_chart(self, df: pd.DataFrame,
                               x_column: str,
                               open_col: str, high_col: str,
                               low_col: str, close_col: str,
                               config: Optional[Dict] = None) -> go.Figure:
        """Create a candlestick chart for OHLC data."""
        config = {**self.default_config, **(config or {})}
        
        fig = go.Figure(data=go.Candlestick(
            x=df[x_column],
            open=df[open_col],
            high=df[high_col],
            low=df[low_col],
            close=df[close_col],
            name="OHLC"
        ))
        
        self._apply_layout(fig, config, x_column, [open_col, high_col, low_col, close_col])
        return fig
    
    def create_heatmap(self, df: pd.DataFrame,
                      x_column: str,
                      y_column: str,
                      z_column: str,
                      config: Optional[Dict] = None) -> go.Figure:
        """Create a heatmap."""
        config = {**self.default_config, **(config or {})}
        
        # Pivot data for heatmap
        pivot_data = df.pivot_table(
            values=z_column,
            index=y_column,
            columns=x_column,
            aggfunc='mean'
        )
        
        fig = go.Figure(data=go.Heatmap(
            z=pivot_data.values,
            x=pivot_data.columns,
            y=pivot_data.index,
            colorscale=config.get('color_palette', 'Viridis'),
            text=pivot_data.values,
            texttemplate="%{text:.2f}",
            textfont={"size": 10},
            hoverongaps=False
        ))
        
        self._apply_layout(fig, config, x_column, [z_column])
        return fig
    
    def create_multi_axis_plot(self, df: pd.DataFrame,
                              x_column: str,
                              left_y_columns: List[str],
                              right_y_columns: List[str],
                              config: Optional[Dict] = None) -> go.Figure:
        """Create a plot with multiple y-axes."""
        config = {**self.default_config, **(config or {})}
        
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        colors = self._get_colors(
            len(left_y_columns) + len(right_y_columns),
            config.get('color_palette', 'Default')
        )
        
        color_idx = 0
        
        # Add left y-axis traces
        for col in left_y_columns:
            fig.add_trace(
                go.Scatter(
                    x=df[x_column],
                    y=df[col],
                    mode='lines+markers',
                    name=col,
                    line=dict(color=colors[color_idx % len(colors)]),
                    yaxis='y'
                ),
                secondary_y=False
            )
            color_idx += 1
        
        # Add right y-axis traces
        for col in right_y_columns:
            fig.add_trace(
                go.Scatter(
                    x=df[x_column],
                    y=df[col],
                    mode='lines+markers',
                    name=col,
                    line=dict(color=colors[color_idx % len(colors)]),
                    yaxis='y2'
                ),
                secondary_y=True
            )
            color_idx += 1
        
        # Update layout
        fig.update_layout(
            title=config.get('title', 'Multi-Axis Time Series'),
            width=config.get('width', 800),
            height=config.get('height', 500)
        )
        
        fig.update_xaxes(title_text=x_column)
        fig.update_yaxes(title_text=", ".join(left_y_columns), secondary_y=False)
        fig.update_yaxes(title_text=", ".join(right_y_columns), secondary_y=True)
        
        return fig
    
    def create_subplot_grid(self, df: pd.DataFrame,
                           x_column: str,
                           y_columns: List[str],
                           config: Optional[Dict] = None) -> go.Figure:
        """Create a grid of subplots."""
        config = {**self.default_config, **(config or {})}
        
        n_plots = len(y_columns)
        cols = min(2, n_plots)
        rows = (n_plots + cols - 1) // cols
        
        fig = make_subplots(
            rows=rows,
            cols=cols,
            subplot_titles=y_columns,
            vertical_spacing=0.1,
            horizontal_spacing=0.1
        )
        
        colors = self._get_colors(n_plots, config.get('color_palette', 'Default'))
        
        for i, col in enumerate(y_columns):
            row = (i // cols) + 1
            col_pos = (i % cols) + 1

            fig.add_trace(
                go.Scatter(
                    x=df[x_column],
                    y=df[col],
                    mode='lines+markers',
                    name=col,
                    line=dict(color=colors[i % len(colors)]),
                    showlegend=False
                ),
                row=row,
                col=col_pos
            )
        
        fig.update_layout(
            title=config.get('title', 'Multiple Time Series'),
            width=config.get('width', 1000),
            height=config.get('height', 600)
        )
        
        return fig
    
    def _get_colors(self, n_colors: int, palette_name: str) -> List[str]:
        """Get a list of colors from the specified palette."""
        if palette_name in self.COLOR_PALETTES:
            colors = self.COLOR_PALETTES[palette_name]
            # Repeat colors if we need more than available
            return (colors * ((n_colors // len(colors)) + 1))[:n_colors]
        else:
            # Default to Plotly colors
            return px.colors.qualitative.Plotly[:n_colors]
    
    def _add_transparency(self, color: str, alpha: float) -> str:
        """Add transparency to a color."""
        if color.startswith('#'):
            # Convert hex to rgba
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)
            return f'rgba({r},{g},{b},{alpha})'
        else:
            return color
    
    def _add_trendline(self, fig: go.Figure, x_data: pd.Series, y_data: pd.Series, color: str):
        """Add a trendline to the plot."""
        try:
            # Convert datetime to numeric for trend calculation
            if pd.api.types.is_datetime64_any_dtype(x_data):
                x_numeric = pd.to_numeric(x_data)
            else:
                x_numeric = x_data

            # Remove NaN values
            mask = ~(pd.isna(x_numeric) | pd.isna(y_data))
            x_clean = x_numeric[mask]
            y_clean = y_data[mask]

            if len(x_clean) > 1:
                # Calculate trend line
                z = np.polyfit(x_clean, y_clean, 1)
                p = np.poly1d(z)
    
                fig.add_trace(go.Scatter(
                    x=x_data,
                    y=p(x_numeric),
                    mode='lines',
                    name='Trend',
                    line=dict(dash='dash', color=color, width=1),
                    opacity=0.7
                ))
        except Exception:
            pass  # Skip trendline if calculation fails
    
    def _apply_layout(self, fig: go.Figure, config: Dict, x_column: str, y_columns: List[str]):
        """Apply common layout settings to the figure."""
        fig.update_layout(
            title=config.get('title', f"{', '.join(y_columns)} vs {x_column}"),
            xaxis_title=config.get('x_title', x_column),
            yaxis_title=config.get('y_title', ', '.join(y_columns)),
            width=config.get('width', 800),
            height=config.get('height', 500),
            template=config.get('theme', 'plotly_white'),
            font=dict(size=config.get('font_size', 12)),
            hovermode='x unified' if config.get('unified_hover', True) else 'closest',
            legend=dict(
                orientation=config.get('legend_orientation', 'v'),
                yanchor=config.get('legend_yanchor', 'top'),
                y=config.get('legend_y', 1),
                xanchor=config.get('legend_xanchor', 'left'),
                x=config.get('legend_x', 1.02)
            )
        )
        
        # Update axes
        if config.get('x_range'):
            fig.update_xaxes(range=config['x_range'])
        
        if config.get('y_range'):
            fig.update_yaxes(range=config['y_range'])
        
        if config.get('log_y', False):
            fig.update_yaxes(type="log")
        
        if config.get('log_x', False):
            fig.update_xaxes(type="log")
        
        # Grid settings
        if config.get('show_grid', True):
            fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
            fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
    
    def add_annotations(self, fig: go.Figure, annotations: List[Dict]) -> go.Figure:
        """Add annotations to the plot."""
        for annotation in annotations:
            fig.add_annotation(
                x=annotation.get('x'),
                y=annotation.get('y'),
                text=annotation.get('text', ''),
                showarrow=annotation.get('show_arrow', True),
                arrowhead=annotation.get('arrow_head', 2),
                arrowsize=annotation.get('arrow_size', 1),
                arrowwidth=annotation.get('arrow_width', 2),
                arrowcolor=annotation.get('arrow_color', 'black'),
                font=dict(
                    size=annotation.get('font_size', 12),
                    color=annotation.get('font_color', 'black')
                ),
                bgcolor=annotation.get('bg_color', 'white'),
                bordercolor=annotation.get('border_color', 'black'),
                borderwidth=annotation.get('border_width', 1)
            )
        return fig
    
    def export_plot(self, fig: go.Figure, 
                   filename: str, 
                   format: str = 'png',
                   width: int = 800,
                   height: int = 500,
                   scale: int = 2) -> bytes:
        """
        Export plot to various formats.
        
        Args:
            fig: Plotly Figure object
            filename: Filename for export
            format: Export format ('png', 'jpeg', 'svg', 'pdf', 'html')
            width: Image width in pixels
            height: Image height in pixels
            scale: Scale factor for raster formats

        Returns:
            Bytes data of the exported file
        """
        if format.lower() == 'html':
            return fig.to_html(include_plotlyjs=True).encode()
        elif format.lower() in ['png', 'jpeg', 'svg', 'pdf']:
            return fig.to_image(
                format=format.lower(),
                width=width,
                height=height,
                scale=scale
            )
        else:
            raise ValueError(f"Unsupported export format: {format}")
