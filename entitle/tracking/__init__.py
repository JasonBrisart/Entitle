"""
Entitle Tracking

Records deployments, forks, and provenance for Entitle-managed software.

All records are written to a single append-only, tamper-evident store
(``entitle.records.RecordStore``). This gives Entitle the deployment tracking,
internal fork management, and provenance/ownership documentation described in the
README, without any cloud service, activation server, or telemetry.

Prior to 0.4.0 this was a single ``entitle/track.py`` module. It was split into a
package so each concern lives on its own:

    tracking/deploy.py       governed deployment recording (checks entitlement)
    tracking/fork.py         documentary fork records
    tracking/provenance.py   documentary provenance/ownership records
    tracking/query.py        read-only listing helpers
    tracking/cli.py          the ``track`` CLI subcommand group

The public functions are re-exported here so existing imports continue to work
by simply pointing at ``entitle.tracking`` instead of ``entitle.track``:

    from entitle.tracking import deploy_from_file, record_fork, record_provenance
"""
from .deploy import count_deployments, deploy_from_file, register_deployment
from .fork import record_fork
from .provenance import record_provenance
from .query import list_records

__all__ = [
    "count_deployments",
    "register_deployment",
    "deploy_from_file",
    "record_fork",
    "record_provenance",
    "list_records",
]
