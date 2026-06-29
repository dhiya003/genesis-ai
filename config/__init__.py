"""Shared runtime configuration package for Genesis AI."""

from .runtime import RuntimeConfig, load_runtime_config
from .logging import configure_logging

__all__ = ["RuntimeConfig", "configure_logging", "load_runtime_config"]
