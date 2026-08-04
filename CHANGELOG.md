# Changelog

All notable changes to Entitle are documented in this file.

Entitle is pure Python with no external dependencies and is designed for
local-first, offline, and air-gapped environments.

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
