"""
Entitle
Software Rights Management for Independent and Offline Environments.

This package contains Entitle's own pure-Python logic: entitlement payloads,
rights evaluation, the tamper-evident record store, and the governed
deployment/fork/provenance/revocation/audit workflows.

Entitlement protection (encryption/authentication) is delegated to the
BrisartSecurityResearch (BSR2) research modules through ``entitle.bsr_adapter``.
BSR2 itself lives in the sibling ``vendor/`` directory and is never modified by
this package.

The package version is not defined here. It is read from the single source of
truth in the repository-root ``version.py`` module, so the package, the CLI, the
GUI, and any release tooling all report the same value.
"""
from pathlib import Path
import sys

# Expose the repository-root version.py as the authoritative __version__ without
# duplicating the string. The root directory is the parent of this package.
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from version import __version__  # noqa: E402  (import after sys.path setup)

__all__ = ["__version__"]
