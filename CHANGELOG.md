# Changelog

All notable changes to Entitle are documented in this file.

Entitle is pure Python with no external dependencies and is designed for
local-first, offline, and air-gapped environments.

---

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
  completely unmodified.

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
- Every shipped `.py` file was diffed byte-for-byte (size, line count, and
  SHA-256) against a fresh export of the live repository with zero
  mismatches.

### Notes
- No changes were required to `entitle_core.py`, `entitle_records.py`,
  `entitle_track.py`, `entitle_revoke.py`, or `entitle_report.py`; all
  governance and tamper-evidence logic in those modules was already correct.
- BrisartSecurityResearch (BSR2) source itself was not modified in any way.
  BSR2 remains an independent, experimental research dependency and should
  continue to be treated as controlled-environment protection unless
  independently reviewed.

---

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
