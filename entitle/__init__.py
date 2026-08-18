"""
Entitle

Software Rights Management for Independent and Offline Environments.

This package contains Entitle's own pure-Python logic: entitlement payloads,
rights evaluation, the tamper-evident record store, and the governed
deployment/fork/provenance/revocation/audit workflows.

Entitlement protection (encryption/authentication) is delegated to the
BrisartSecurityResearch (BSR2) research modules through
`entitle.bsr_adapter`. BSR2 itself lives in the sibling `bsr/` directory and
is never modified by this package.
"""

__version__ = "0.3.1"