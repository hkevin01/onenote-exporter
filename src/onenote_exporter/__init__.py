"""onenote_exporter public package interface."""

# Re-export core submodules for convenience (import onenote_exporter.graph ...)
from . import auth, cli, config, exporter, graph, utils

__all__ = [
    "auth",
    "cli",
    "config",
    "exporter",
    "graph",
    "utils",
]

try:  # optional catalog support
    from . import db  # type: ignore  # noqa: F401

    __all__.append("db")
except (ImportError, OSError):  # pragma: no cover
    pass

__all__ = [
    "auth",
    "cli",
    "config",
    "exporter",
    "graph",
    "utils",
]

try:  # optional module
    from . import db as _db  # noqa: F401
    __all__.append("db")
except (ImportError, OSError):  # pragma: no cover
    pass

__version__ = "0.1.0"
