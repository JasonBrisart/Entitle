"""
Entitle Track
Records deployments, forks, and provenance for Entitle-managed software.

All records are written to a single append-only, tamper-evident store
(entitle_records.RecordStore). This gives Entitle the deployment tracking,
internal fork management, and provenance/ownership documentation described
in the README, without any cloud service, activation server, or telemetry.

Deployment records are additionally governed: a deployment is only recorded
if a valid Entitle entitlement grants can_run, the entitlement has not been
revoked, and the entitlement's deployment_limit is not already reached.

Examples:
    Record a governed deployment:
        python entitle_track.py deploy ^
            --issuer JasonBrisart ^
            --subject ResearchLabA ^
            --product EntitleDemo ^
            --master-key "change-this-master-key-change-this-master-key" ^
            --entitlement entitlements/lab_a.entitle ^
            --host lab-a-node-01 ^
            --environment air-gapped ^
            --store records/entitle_records.log

    Record an internal fork:
        python entitle_track.py fork ^
            --product EntitleDemo ^
            --source-version 1.4.0 ^
            --fork-name lab-a-custom ^
            --maintainer ResearchLabA ^
            --store records/entitle_records.log

    Record provenance / ownership:
        python entitle_track.py provenance ^
            --product EntitleDemo ^
            --origin JasonBrisart ^
            --version 1.4.0 ^
            --custodian ResearchLabA ^
            --store records/entitle_records.log

    List records of a given type:
        python entitle_track.py list --type deployment --store records/entitle_records.log
"""

import argparse
import json

from entitle_records import RecordStore


def count_deployments(store, product_id, subject_id, entitlement_id):
    def matches(record):
        data = record.get("data", {})
        return (
            data.get("product_id") == product_id
            and data.get("subject_id") == subject_id
            and data.get("entitlement_id") == entitlement_id
        )

    return len(store.filter(record_type="deployment", predicate=matches))


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

    from entitle_revoke import is_revoked

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
        "deployment",
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


def cmd_deploy(args):
    from entitle_bsr_adapter import verify_protected_entitlement

    entitlement = verify_protected_entitlement(
        path=args.entitlement,
        master_key=args.master_key.encode("utf-8"),
        expected_product_id=args.product,
        issuer_id=args.issuer,
        subject_id=args.subject,
    )
    store = RecordStore(args.store)
    outcome = register_deployment(
        store=store,
        entitlement=entitlement,
        host=args.host,
        environment=args.environment,
        notes=args.notes,
    )
    print(json.dumps(outcome, indent=2, ensure_ascii=False))


def cmd_fork(args):
    store = RecordStore(args.store)
    record = store.append(
        "fork",
        {
            "product_id": args.product,
            "source_version": args.source_version,
            "fork_name": args.fork_name,
            "maintainer": args.maintainer,
            "environment": args.environment,
            "notes": args.notes,
        },
    )
    print(json.dumps(record, indent=2, ensure_ascii=False))


def cmd_provenance(args):
    store = RecordStore(args.store)
    record = store.append(
        "provenance",
        {
            "product_id": args.product,
            "origin": args.origin,
            "version": args.version,
            "previous_version": args.previous_version,
            "custodian": args.custodian,
            "notes": args.notes,
        },
    )
    print(json.dumps(record, indent=2, ensure_ascii=False))


def cmd_list(args):
    store = RecordStore(args.store)
    records = store.filter(record_type=args.type)
    print(json.dumps(records, indent=2, ensure_ascii=False))


def build_parser():
    parser = argparse.ArgumentParser(
        description="Record deployments, forks, and provenance for Entitle."
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
    deploy.set_defaults(func=cmd_deploy)

    fork = subparsers.add_parser("fork", help="Record an internal fork.")
    fork.add_argument("--product", required=True)
    fork.add_argument("--source-version", required=True)
    fork.add_argument("--fork-name", required=True)
    fork.add_argument("--maintainer", required=True)
    fork.add_argument("--environment", default=None)
    fork.add_argument("--notes", default=None)
    fork.add_argument("--store", required=True, help="Record store file path.")
    fork.set_defaults(func=cmd_fork)

    provenance = subparsers.add_parser("provenance", help="Record provenance/ownership.")
    provenance.add_argument("--product", required=True)
    provenance.add_argument("--origin", required=True)
    provenance.add_argument("--version", required=True)
    provenance.add_argument("--previous-version", default=None)
    provenance.add_argument("--custodian", required=True)
    provenance.add_argument("--notes", default=None)
    provenance.add_argument("--store", required=True, help="Record store file path.")
    provenance.set_defaults(func=cmd_provenance)

    listing = subparsers.add_parser("list", help="List records of a type.")
    listing.add_argument(
        "--type",
        default=None,
        help="deployment, fork, or provenance. Omit for all records.",
    )
    listing.add_argument("--store", required=True, help="Record store file path.")
    listing.set_defaults(func=cmd_list)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()