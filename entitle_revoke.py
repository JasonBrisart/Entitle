"""
Entitle Revoke

Offline revocation for Entitle entitlements.
"""

import argparse
import json

from entitle_records import RecordStore


def revocation_status(store, entitlement_id):
    revoked = False
    last_record = None
    for record in store.read_all():
        record_type = record.get("record_type")
        if record_type not in ("revocation", "reinstatement"):
            continue
        if record.get("data", {}).get("entitlement_id") != entitlement_id:
            continue
        revoked = record_type == "revocation"
        last_record = record
    return {
        "entitlement_id": entitlement_id,
        "revoked": revoked,
        "last_record": last_record,
    }


def is_revoked(store, entitlement_id):
    return revocation_status(store, entitlement_id)["revoked"]


def revoke(store, entitlement_id, issuer_id=None, product_id=None, reason=None):
    return store.append(
        "revocation",
        {
            "entitlement_id": entitlement_id,
            "issuer_id": issuer_id,
            "product_id": product_id,
            "reason": reason,
        },
    )


def reinstate(store, entitlement_id, issuer_id=None, product_id=None, reason=None):
    return store.append(
        "reinstatement",
        {
            "entitlement_id": entitlement_id,
            "issuer_id": issuer_id,
            "product_id": product_id,
            "reason": reason,
        },
    )


def cmd_revoke(args):
    store = RecordStore(args.store)
    record = revoke(
        store,
        entitlement_id=args.entitlement_id,
        issuer_id=args.issuer,
        product_id=args.product,
        reason=args.reason,
    )
    print(json.dumps(record, indent=2, ensure_ascii=False))


def cmd_reinstate(args):
    store = RecordStore(args.store)
    record = reinstate(
        store,
        entitlement_id=args.entitlement_id,
        issuer_id=args.issuer,
        product_id=args.product,
        reason=args.reason,
    )
    print(json.dumps(record, indent=2, ensure_ascii=False))


def cmd_check(args):
    store = RecordStore(args.store)
    status = revocation_status(store, args.entitlement_id)
    print(json.dumps(status, indent=2, ensure_ascii=False))
    print()
    print("REVOKED" if status["revoked"] else "ACTIVE")


def build_parser():
    parser = argparse.ArgumentParser(
        description="Revoke, reinstate, or check Entitle entitlements offline."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    rev = subparsers.add_parser("revoke", help="Record a revocation.")
    rev.add_argument("--entitlement-id", required=True)
    rev.add_argument("--issuer", default=None)
    rev.add_argument("--product", default=None)
    rev.add_argument("--reason", default=None)
    rev.add_argument("--store", required=True, help="Record store file path.")
    rev.set_defaults(func=cmd_revoke)

    rei = subparsers.add_parser("reinstate", help="Record a reinstatement.")
    rei.add_argument("--entitlement-id", required=True)
    rei.add_argument("--issuer", default=None)
    rei.add_argument("--product", default=None)
    rei.add_argument("--reason", default=None)
    rei.add_argument("--store", required=True, help="Record store file path.")
    rei.set_defaults(func=cmd_reinstate)

    chk = subparsers.add_parser("check", help="Check revocation status.")
    chk.add_argument("--entitlement-id", required=True)
    chk.add_argument("--store", required=True, help="Record store file path.")
    chk.set_defaults(func=cmd_check)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
