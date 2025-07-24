"""Plot subpackage.

This sub-package houses reusable plotting utilities in smaller, focused
modules.  The public surface is deliberately minimal at this stage; we only
re-export the `BasePlotter` so existing code can migrate gradually.
"""

from .base import BasePlotter  # noqa: F401
from .line import create_line_chart  # noqa: F401
from .scatter import create_scatter_plot  # noqa: F401
from .bar import create_bar_chart  # noqa: F401
from .area import create_area_chart  # noqa: F401
from .box import create_box_plot  # noqa: F401

# Factory registry so callers can do utils.plot.create_plot('line', ...)
import config as _cfg  # local config

COLOR_PALETTES = _cfg.COLOR_PALETTES  # noqa: N806, re-export for pages

_CREATORS = {
    "line": create_line_chart,
    "scatter": create_scatter_plot,
    "bar": create_bar_chart,
    "area": create_area_chart,
    "box": create_box_plot,
}

def create_plot(plot_type: str, *args, **kwargs):
    """Factory helper that dispatches to the right builder by *plot_type*."""
    try:
        return _CREATORS[plot_type.lower()](*args, **kwargs)
    except KeyError as exc:
        raise ValueError(f"Unsupported plot type: {plot_type}") from exc
