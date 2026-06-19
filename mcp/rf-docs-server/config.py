"""
config.py

Shared configuration for rf-docs-server: logging setup, path resolution,
and load-time settings. Mirrors the config.py convention already used by
robocop-server in this project.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logger = logging.getLogger("rf-docs-server")
if not logger.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(
        logging.Formatter("%(asctime)s [%(name)s] %(levelname)s: %(message)s")
    )
    logger.addHandler(_handler)
    logger.setLevel(os.environ.get("RF_DOCS_LOG_LEVEL", "INFO"))

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SERVER_DIR = Path(__file__).parent.resolve()
DEFAULT_SPECS_DIR = SERVER_DIR / "specs"


def resolve_path(path_str: str, base: Optional[Path] = None) -> Path:
    """
    Resolve a possibly-relative path string against `base` (default: this
    server's directory), expanding `~` and environment variables. Used so
    that paths supplied via env vars or config behave consistently
    regardless of the caller's current working directory.
    """
    expanded = os.path.expandvars(os.path.expanduser(path_str))
    p = Path(expanded)
    if p.is_absolute():
        return p.resolve()
    return ((base or SERVER_DIR) / p).resolve()


class Config:
    """
    Runtime configuration, overridable via environment variables:

      RF_DOCS_SPECS_DIR   - directory containing generated libspec JSON files
                             (default: <server_dir>/specs)
      RF_DOCS_LOG_LEVEL    - logging level (default: INFO)
      RF_DOCS_FUZZY_SEARCH - "1"/"0", whether search_keywords falls back to
                             fuzzy matching when no token overlap is found
                             (default: 1)
    """

    def __init__(self) -> None:
        self.specs_dir: Path = resolve_path(
            os.environ.get("RF_DOCS_SPECS_DIR", str(DEFAULT_SPECS_DIR))
        )
        self.fuzzy_search: bool = os.environ.get("RF_DOCS_FUZZY_SEARCH", "1") != "0"

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"Config(specs_dir={self.specs_dir}, fuzzy_search={self.fuzzy_search})"


_config: Optional[Config] = None


def get_config() -> Config:
    """Lazily construct and cache the process-wide Config instance."""
    global _config
    if _config is None:
        _config = Config()
        logger.debug("Loaded config: %s", _config)
    return _config
