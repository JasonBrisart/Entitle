"""
Entitle Constants

Single source of truth for the record_type strings used throughout the
tamper-evident record store (entitle.records.RecordStore).

Previously these were duplicated as plain string literals across
entitle/track.py, entitle/revoke.py, and entitle/report.py. Centralizing
them here means adding a new record type (or renaming one) only requires a
change in one place, and a typo in a record_type string becomes a NameError
at import time instead of a silent no-op filter that matches nothing.
"""

RECORD_TYPE_DEPLOYMENT = "deployment"
RECORD_TYPE_FORK = "fork"
RECORD_TYPE_PROVENANCE = "provenance"
RECORD_TYPE_REVOCATION = "revocation"
RECORD_TYPE_REINSTATEMENT = "reinstatement"

ALL_RECORD_TYPES = (
    RECORD_TYPE_DEPLOYMENT,
    RECORD_TYPE_FORK,
    RECORD_TYPE_PROVENANCE,
    RECORD_TYPE_REVOCATION,
    RECORD_TYPE_REINSTATEMENT,
)
