# pylk/__init__.py
__all__ = ["app", "main_window"]

try:
    from ._version import version as __version__
except ImportError:
    __version__ = "unknown"
