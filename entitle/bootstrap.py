"""
Entitle Bootstrap

Adds the sibling `bsr/` directory (BrisartSecurityResearch, used completely
unmodified) to `sys.path` so its flat, top-level imports
(`from brisart_security_primitives import ...`) resolve correctly.

BSR2's own modules are not a Python package and do not use relative imports,
so `bsr/` cannot be imported as `import bsr` or `from bsr import ...`. It
must be added to `sys.path` directly, as its own path entry, with its
`.py` files sitting flat inside it.

Every Entitle entry point (the CLI in `main.py`, the GUI in `gui/app.py`,
and `examples/protected_app_example.py`) calls `ensure_bsr_on_path()` before
importing anything from `entitle.bsr_adapter`.
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BSR_DIR = REPO_ROOT / "bsr"

_done = False


def ensure_bsr_on_path():
    """Idempotently add the bsr/ directory to sys.path."""
    global _done
    if _done:
        return
    bsr_path = str(BSR_DIR)
    if not BSR_DIR.is_dir():
        raise FileNotFoundError(
            f"Expected the BrisartSecurityResearch (BSR2) directory at "
            f"'{bsr_path}', but it does not exist. Place the unmodified "
            f"BSR2 .py files there before running Entitle."
        )
    if bsr_path not in sys.path:
        sys.path.insert(0, bsr_path)
    _done = True