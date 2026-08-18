# Changelog
All notable changes to Entitle are documented in this file.
Entitle is pure Python with no external dependencies and is designed for
local-first, offline, and air-gapped environments.

## [0.3.1] - 2026-08-18
This release is a follow-up architecture cleanup pass on top of 0.3.0's
package restructure. No governance logic, record-store semantics, or
entitlement behavior changed.

### Added
- `entitle/constants.py` — single source of truth for the five
  `record_type` strings (`deployment`, `fork`, `provenance`, `revocation`,
  `reinstatement`) used throughout the tamper-evident record store. These
  were previously duplicated as plain string literals across
  `entitle/track.py`, `entitle/revoke.py`, and `entitle/report.py`.
- `gui/widgets.py` — the shared `FormFrame` label/entry/checkbox helper used
  by every GUI tab, extracted out of the former single-file GUI.
- `gui/tabs/` — the GUI's six tabs (Issue, Verify, Deploy, Fork /
  Provenance, Revoke / Reinstate, Audit Report) are now individual plug-in
  modules (`gui/tabs/issue_tab.py`, `verify_tab.py`, `deploy_tab.py`,
  `fork_provenance_tab.py`, `revoke_tab.py`, `report_tab.py`), each exposing
  a `TAB_TITLE` string and a `build(parent, app)` function. `gui/app.py`
  now only builds the main window and loads tabs from an explicit
  `TAB_MODULES` registry — it has no per-tab logic of its own. Adding a new
  tab means adding one new file plus one line in `TAB_MODULES`; no other
  file needs to change.

### Changed
- `gui/app.py` reduced from a single 407-line file containing all six tabs
  to a 110-line core engine that only builds the window, the shared output
  pane, and the tab registry.
- `entitle/track.py`, `entitle/revoke.py`, and `entitle/report.py` now
  import their `record_type` strings from `entitle/constants.py` instead of
  repeating literal strings, so a typo in a record type now fails at import
  time (`ImportError`/`NameError`) instead of silently matching nothing.
- `main.py`'s command dispatch replaced an `if`/`elif` chain with a
  `COMMAND_MODULES` dict mapping command name to dotted module path. Adding
  a new top-level CLI command (beyond `issue`/`verify`/`track`/`revoke`/
  `report`/`gui`) now means adding one dict entry instead of another
  `elif` branch.

### Verified
- The full CLI lifecycle (issue, verify, deploy with `deployment_limit`
  enforcement and refusal, fork, provenance, revoke, deploy-while-revoked
  refusal, reinstate, check, audit report) was re-run end-to-end through
  `main.py` after the constants and dispatch-table changes, with identical
  results to 0.3.0.
- The modularized GUI was re-verified with the same headless test harness
  used for 0.3.0: instantiate the real `EntitleApp`, confirm all six
  registered tab plug-ins appear in the notebook, and click through every
  tab's button (issue → verify → deploy ×2 → 3rd deploy refused → fork →
  provenance → revoke → deploy-while-revoked refused → reinstate → check →
  report). All 11 assertions passed against the real backend. As before,
  actual on-screen rendering should be confirmed on a machine with a
  working Tkinter/Tk installation.

## [0.3.0] - 2026-08-18
This release restructures Entitle from a flat collection of scripts into a
proper package with a single command-line entry point, and adds a first
Tkinter GUI covering every core workflow. No governance logic, record-store
semantics, or entitlement behavior changed — this is an architecture and
usability release, not a behavior release.

### Added
- `main.py` — single CLI entry point. Replaces running each `entitle_*.py`
  script directly. Dispatches to `issue`, `verify`, `track`, `revoke`,
  `report`, and `gui` subcommands, e.g. `python main.py issue ...`,
  `python main.py track deploy ...`.
- `entitle/` — Entitle's own logic, reorganized into a proper Python
  package (`core.py`, `records.py`, `bsr_adapter.py`, `issue.py`,
  `verify.py`, `track.py`, `revoke.py`, `report.py`, `bootstrap.py`).
  Internal imports were converted from flat (`from entitle_core import ...`)
  to package-relative (`from .core import ...`).
- `entitle/bootstrap.py` — adds the sibling `bsr/` directory to `sys.path`
  so BrisartSecurityResearch's flat, top-level imports
  (`from brisart_security_primitives import ...`) resolve correctly from
  its new subdirectory location, without modifying a single line of BSR2.
  Every entry point (CLI, GUI, example) calls this before importing
  `entitle.bsr_adapter`.
- `bsr/` — BrisartSecurityResearch (BSR2) now lives in its own directory.
  The four `.py` files are byte-for-byte unchanged from the flat layout;
  only their location moved.
- Business logic extracted from CLI argument parsing in every `entitle/`
  module, e.g. `issue_entitlement(...)`, `verify_entitlement(...)`,
  `deploy_from_file(...)`, `record_fork(...)`, `record_provenance(...)`,
  `build_report_for_path(...)`. Each CLI subcommand is now a thin wrapper
  around a plain function with the same name and keyword arguments the GUI
  calls directly — the CLI and GUI can never drift out of sync with each
  other because they share one implementation.
- `gui/app.py` — a first Tkinter GUI. Tabs for Issue, Verify, Deploy,
  Fork / Provenance, Revoke / Reinstate / Check, and Audit Report. Every
  button calls directly into the same `entitle.*` functions used by the
  CLI. Requires only the Python standard library. Launch with
  `python main.py gui` or `python gui/app.py`.
- `examples/protected_app_example.py` — moved into its own directory,
  updated for the new package layout, and hardened to print a friendly
  message with a working example command when the demo entitlement file is
  missing, instead of crashing with an uncaught `FileNotFoundError`.

### Changed
- `protected_app_example.py` → `examples/protected_app_example.py`.
- Running an Entitle module directly as a script (e.g.
  `python entitle/issue.py`) is no longer supported, because its imports
  are now package-relative. Use `python main.py issue ...` (or
  `python -m entitle.issue ...`) instead.

### Verified
- The full lifecycle (issue, verify, deploy with `deployment_limit`
  enforcement and refusal, fork, provenance, revoke, deploy-while-revoked
  refusal, reinstate, check, audit report, hash-chain tamper detection) was
  re-run end-to-end through `main.py` in a clean directory with identical
  results to the pre-restructure flat layout.
- Every function the GUI calls was cross-checked against the real
  `entitle.*` function signatures with `inspect.signature`, and the GUI's
  button callbacks were exercised end-to-end against the real backend
  (issue → verify → deploy ×2 → 3rd deploy refused → fork → provenance →
  revoke → deploy-while-revoked refused → reinstate → check → report) using
  a headless test harness, since this development environment has no
  `_tkinter` extension available to open a real window. The GUI's actual
  on-screen rendering should be confirmed on a machine with a working
  Tkinter/Tk installation (standard on Windows, macOS, and most Linux
  desktop distributions) before relying on it day-to-day.
- BSR2's four `.py` files were confirmed byte-for-byte identical (SHA-256)
  before and after the move into `bsr/`.

### Notes
- No changes were made to any BrisartSecurityResearch (BSR2) source file.
  BSR2 remains an independent, experimental research dependency and should
  continue to be treated as controlled-environment protection unless
  independently reviewed.
- Runtime data directories (`entitlements/`, `records/`, `reports/`) keep
  their previous meaning and location at the repository root; no default
  store path was introduced, preserving the existing "operator always
  specifies `--store` explicitly" design principle.

## [0.2.1] - 2026-08-18
This release fixes integration bugs between `entitle_bsr_adapter.py` and the
real BrisartSecurityResearch (BSR2) module that prevented `entitle_issue.py`
from running at all against an unmodified BSR2 checkout. No governance logic,
record-store behavior, or entitlement semantics changed; every fix is
isolated to the BSR2 adapter wiring layer.

### Fixed
- `entitle_bsr_adapter.py` imported `BrisartSecurityDRBG`, `encrypt_envelope`,
  and `decrypt_envelope`, but the real BSR2 module exports `BrisartDRBG`,
  `encrypt`, and `decrypt`. Import aliasing was added so BSR2 source files
  can be used completely unmodified.
- `protect_entitlement_payload()` called BSR2's `encrypt()` with a `drbg=`
  keyword argument, but BSR2 names that parameter `rng`. Calls were updated
  to `rng=drbg`.
- `make_context()` returned `bytes`, but BSR2's `encrypt()` and `decrypt()`
  both require `context` to be a `str`. `make_context()` now returns a
  string.
- Confirmed the README's suggested `bsr/` subfolder layout does not work as
  written: BSR2's own modules (`brisart_security_drbg.py`,
  `brisart_security_envelope.py`) use flat imports
  (`from brisart_security_primitives import ...`) that cannot resolve from
  inside a subpackage without modifying BSR2 itself. Documented that BSR2
  source files must be placed flat, beside the Entitle source files,
  completely unmodified. (Superseded in 0.3.0 by
  `entitle.bootstrap.ensure_bsr_on_path()`, which adds `bsr/` to `sys.path`
  directly so the flat layout can live in its own subdirectory.)

### Verified
- Every known-answer vector shipped with BrisartSecurityResearch (hash, MAC,
  stream, DRBG output, envelope decrypt, and a deterministic envelope
  re-encrypt) was reproduced byte-for-byte against the unmodified BSR2
  source, confirming the cryptographic primitive layer was untouched and
  correct throughout.
- The full lifecycle was exercised end-to-end in a clean environment:
  issue, verify, governed deploy (including `deployment_limit` enforcement
  and refusal), fork, provenance, revoke, reinstate, and audit reporting.
- Hash-chain tamper detection was confirmed directly: a manually corrupted
  historical record was correctly flagged by `verify_chain()`, with the
  exact broken record index reported.

### Notes
- No changes were required to `entitle_core.py`, `entitle_records.py`,
  `entitle_track.py`, `entitle_revoke.py`, or `entitle_report.py`; all
  governance and tamper-evidence logic in those modules was already correct.
- BrisartSecurityResearch (BSR2) source itself was not modified in any way.
  BSR2 remains an independent, experimental research dependency and should
  continue to be treated as controlled-environment protection unless
  independently reviewed.

## [0.2.0] - 2026-08-04
This release brings the implementation in line with the README by adding the
deployment, fork, provenance, revocation, and audit capabilities that were
previously described but not yet built. All new tooling is pure standard
library and writes to a single local, tamper-evident record store.

### Added
- `entitle_records.py` — append-only, hash-chained record store. Each entry is
  linked to the previous one through a SHA-256 chain, so any edit, deletion, or
  reordering of earlier records is detectable via `verify_chain()`.
- `entitle_track.py` — record deployments, internal forks, and provenance /
  ownership to the shared store. Includes `deploy`, `fork`, `provenance`, and
  `list` subcommands.
- Governed deployments: `register_deployment` only records a deployment when the
  entitlement verifies, grants `can_run`, is not revoked, and its
  `deployment_limit` has not been reached.
- `entitle_revoke.py` — offline revocation with `revoke`, `reinstate`, and
  `check` subcommands. Revocation status is derived from the record log, so an
  entitlement can be revoked and later reinstated while preserving full history.
- `entitle_report.py` — audit and reporting over the record store, with text or
  JSON output. Summarizes records by type and deployments by product, and
  verifies the tamper-evident hash chain across the whole store.

### Changed
- `entitle_track.py` deployment gate now consults `entitle_revoke.is_revoked`
  before recording, so revoked entitlements are refused for new deployments.
- `README.md` rewritten to document the actual tools with runnable CLI examples,
  and to add Requirements, Project Layout, Deployment Tracking rules, Revocation
  & Reinstatement, and the Tamper-Evident Record Store.

### Removed
- Dropped the unimplemented **License Management** feature section from the
  README so documentation matches shipped functionality.

### Notes
- The record store path is always explicit (`--store`); there is no default
  location by design, keeping record placement fully under operator control.
- Entitlement protection continues to rely on the experimental
  BrisartSecurityResearch (BSR) modules via `entitle_bsr_adapter.py`. Treat as
  controlled-environment protection unless independently reviewed.