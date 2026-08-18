"""
Entitle Track

Records deployments, forks, and provenance for Entitle-managed software.

All records are written to a single append-only, tamper-evident store
(entitle.records.RecordStore). This gives Entitle the deployment tracking,
internal fork management, and provenance/ownership documentation described
in the README, without any cloud service, activation server, or telemetry.

Deployment records are additionally governed: a deployment is only recorded
if a valid Entitle entitlement grants can_run, the entitlement has not been
revoked, and the entitlement's deployment_limit is not already reached.

Example:
    python main.py track deploy --issuer JasonBrisart --subject ResearchLabA \
        --product EntitleDemo --master-key "..." \
        --entitlement entitlements/lab_a.entitle --host lab-a-node-01 \
        --environment air-gapped --store records/entitle_records.log
"""

import argparse
import json

from .constants import RECORD_TYPE_DEPLOYMENT, RECORD_TYPE_FORK, RECORD_TYPE_PROVENANCE
from .records import RecordStore


def count_deployments(store, product_id, subject_id, entitlement_id):
    def matches(record):
        data = record.get("data", {})
        return (
            data.get("product_id") == product_id
            and data.get("subject_id") == subject_id
            and data.get("entitlement_id") == entitlement_id
        )
    return len(store.filter(record_type=RECORD_TYPE_DEPLOYMENT, predicate=matches))


def register_deployment(store, entitlement, host, environment=None, notes=None):
    """
    Record a deployment if the entitlement authorizes it.

    Returns a result dict describing whether the deployment was recorded,
    the reason, and (when recorded) the resulting record.
    """
    if not entitlement.allowed:
        return {
            "recorded": False,
            "reason": f"entitlement_denied:{entitlement.reason}",
            "record": None,
        }
    if not entitlement.has_right("can_run"):
        return {
            "recorded": False,
            "reason": "run_right_not_granted",
            "record": None,
        }

    product_id = entitlement.payload.get("product_id")
    subject_id = entitlement.payload.get("subject_id")
    entitlement_id = entitlement.payload.get("entitlement_id")

    from .revoke import is_revoked
    if is_revoked(store, entitlement_id):
        return {
            "recorded": False,
            "reason": "entitlement_revoked",
            "record": None,
        }

    limit = entitlement.get_limit("deployment_limit", default=1)
    used = count_deployments(store, product_id, subject_id, entitlement_id)
    if limit is not None and used >= limit:
        return {
            "recorded": False,
            "reason": "deployment_limit_reached",
            "record": None,
            "deployment_limit": limit,
            "deployments_used": used,
        }

    record = store.append(
        RECORD_TYPE_DEPLOYMENT,
        {
            "product_id": product_id,
            "subject_id": subject_id,
            "issuer_id": entitlement.payload.get("issuer_id"),
            "entitlement_id": entitlement_id,
            "host": host,
            "environment": environment,
            "notes": notes,
        },
    )
    return {
        "recorded": True,
        "reason": "deployment_recorded",
        "record": record,
        "deployment_limit": limit,
        "deployments_used": used + 1,
    }


def deploy_from_file(
    *,
    issuer,
    subject,
    product,
    master_key,
    entitlement_path,
    host,
    store,
    environment=None,
    notes=None,
):
    """
    Verify a protected entitlement file and, if it authorizes it, record a
    governed deployment. Single source of truth used by both the CLI and
    the GUI.
    """
    from .bsr_adapter import verify_protected_entitlement
    master_key_bytes = master_key if isinstance(master_key, bytes) else master_key.encode("utf-8")
    entitlement = verify_protected_entitlement(
        path=entitlement_path,
        master_key=master_key_bytes,
        expected_product_id=product,
        issuer_id=issuer,
        subject_id=subject,
    )
    record_store = RecordStore(store)
    return register_deployment(
        store=record_store,
        entitlement=entitlement,
        host=host,
        environment=environment,
        notes=notes,
    )


def record_fork(*, store, product, source_version, fork_name, maintainer, environment=None, notes=None):
    record_store = RecordStore(store)
    return record_store.append(
        RECORD_TYPE_FORK,
        {
            "product_id": product,
            "source_version": source_version,
            "fork_name": fork_name,
            "maintainer": maintainer,
            "environment": environment,
            "notes": notes,
        },
    )


def record_provenance(*, store, product, origin, version, custodian, previous_version=None, notes=None):
    record_store = RecordStore(store)
    return record_store.append(
        RECORD_TYPE_PROVENANCE,
        {
            "product_id": product,
            "origin": origin,
            "version": version,
            "previous_version": previous_version,
            "custodian": custodian,
            "notes": notes,
        },
    )


def list_records(*, store, record_type=None):
    record_store = RecordStore(store)
    return record_store.filter(record_type=record_type)


def _cmd_deploy(args):
    outcome = deploy_from_file(
        issuer=args.issuer,
        subject=args.subject,
        product=args.product,
        master_key=args.master_key,
        entitlement_path=args.entitlement,
        host=args.host,
        store=args.store,
        environment=args.environment,
        notes=args.notes,
    )
    print(json.dumps(outcome, indent=2, ensure_ascii=False))


def _cmd_fork(args):
    record = record_fork(
        store=args.store,
        product=args.product,
        source_version=args.source_version,
        fork_name=args.fork_name,
        maintainer=args.maintainer,
        environment=args.environment,
        notes=args.notes,
    )
    print(json.dumps(record, indent=2, ensure_ascii=False))


def _cmd_provenance(args):
    record = record_provenance(
        store=args.store,
        product=args.product,
        origin=args.origin,
        version=args.version,
        custodian=args.custodian,
        previous_version=args.previous_version,
        notes=args.notes,
    )
    print(json.dumps(record, indent=2, ensure_ascii=False))


def _cmd_list(args):
    records = list_records(store=args.store, record_type=args.type)
    print(json.dumps(records, indent=2, ensure_ascii=False))


def build_parser():
    parser = argparse.ArgumentParser(
        prog="track",
        description="Record deployments, forks, and provenance for Entitle.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    deploy = subparsers.add_parser("deploy", help="Record a governed deployment.")
    deploy.add_argument("--issuer", required=True)
    deploy.add_argument("--subject", required=True)
    deploy.add_argument("--product", required=True)
    deploy.add_argument("--master-key", required=True)
    deploy.add_argument("--entitlement", required=True, help="Protected .entitle file.")
    deploy.add_argument("--host", required=True, help="Deployment host or node ID.")
    deploy.add_argument("--environment", default=None)
    deploy.add_argument("--notes", default=None)
    deploy.add_argument("--store", required=True, help="Record store file path.")
    deploy.set_defaults(func=_cmd_deploy)

    fork = subparsers.add_parser("fork", help="Record an internal fork.")
    fork.add_argument("--product", required=True)
    fork.add_argument("--source-version", required=True)
    fork.add_argument("--fork-name", required=True)
    fork.add_argument("--maintainer", required=True)
    fork.add_argument("--environment", default=None)
    fork.add_argument("--notes", default=None)
    fork.add_argument("--store", required=True, help="Record store file path.")
    fork.set_defaults(func=_cmd_fork)

    provenance = subparsers.add_parser("provenance", help="Record provenance/ownership.")
    provenance.add_argument("--product", required=True)
    provenance.add_argument("--origin", required=True)
    provenance.add_argument("--version", required=True)
    provenance.add_argument("--previous-version", default=None)
    provenance.add_argument("--custodian", required=True)
    provenance.add_argument("--notes", default=None)
    provenance.add_argument("--store", required=True, help="Record store file path.")
    provenance.set_defaults(func=_cmd_provenance)

    listing = subparsers.add_parser("list", help="List records of a type.")
    listing.add_argument(
        "--type",
        default=None,
        help="deployment, fork, or provenance. Omit for all records.",
    )
    listing.add_argument("--store", required=True, help="Record store file path.")
    listing.set_defaults(func=_cmd_list)

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)
    