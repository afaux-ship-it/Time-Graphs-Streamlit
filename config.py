"""Central configuration constants for the Graph Anything Over Time app.
Keeping all tweakable parameters in one place improves maintainability
and avoids scattering magic numbers throughout the codebase.
"""

# -----------------------------
# File-handling configuration
# -----------------------------
MAX_FILE_SIZE: int = 200  # megabytes

SUPPORTED_EXTENSIONS = {
    ".csv": "CSV",
    ".xlsx": "Excel",
    ".xls": "Excel Legacy",
    ".json": "JSON",
    ".tsv": "TSV",
}

# -----------------------------
# Date-time parsing patterns
# -----------------------------
DATE_PATTERNS = [
    r"\d{4}-\d{2}-\d{2}",       # YYYY-MM-DD
    r"\d{2}/\d{2}/\d{4}",       # MM/DD/YYYY or DD/MM/YYYY
    r"\d{2}-\d{2}-\d{4}",       # MM-DD-YYYY or DD-MM-YYYY
    r"\d{1,2}/\d{1,2}/\d{4}",   # M/D/YYYY
    r"\d{1,2}-\d{1,2}-\d{4}",   # M-D-YYYY
    r"\d{4}/\d{2}/\d{2}",       # YYYY/MM/DD
    r"\d{4}\d{2}\d{2}",         # YYYYMMDD
]

DATETIME_FORMATS = [
    "%Y-%m-%d",
    "%Y/%m/%d",
    "%m/%d/%Y",
    "%d/%m/%Y",
    "%m-%d-%Y",
    "%d-%m-%Y",
    "%Y-%m-%d %H:%M:%S",
    "%Y/%m/%d %H:%M:%S",
    "%m/%d/%Y %H:%M:%S",
    "%d/%m/%Y %H:%M:%S",
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%dT%H:%M:%SZ",
    "%Y-%m-%d %H:%M:%S.%f",
    "%Y%m%d",
    "%d-%b-%Y",
    "%d %b %Y",
    "%B %d, %Y",
    "%b %d, %Y",
    "%d %B %Y",
]

# -----------------------------
# Plotting defaults
# -----------------------------
from plotly import express as _px  # type: ignore

COLOR_PALETTES = {
    "Default": _px.colors.qualitative.Plotly,
    "Viridis": _px.colors.sequential.Viridis,
    "Blues": _px.colors.sequential.Blues,
    "Reds": _px.colors.sequential.Reds,
    "Greens": _px.colors.sequential.Greens,
    "Rainbow": _px.colors.qualitative.Set1,
    "Pastel": _px.colors.qualitative.Pastel,
    "Dark24": _px.colors.qualitative.Dark24,
    "Professional": [
        "#1f77b4",
        "#ff7f0e",
        "#2ca02c",
        "#d62728",
        "#9467bd",
        "#8c564b",
        "#e377c2",
        "#7f7f7f",
        "#bcbd22",
        "#17becf",
    ],
}

DEFAULT_PLOT_CONFIG = {
    "theme": "plotly_white",
    "width": 800,
    "height": 500,
    "font_size": 12,
    "line_width": 2,
    "marker_size": 6,
    "opacity": 0.8,
}
