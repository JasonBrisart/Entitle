"""
Entitle Issue Tool

Creates a protected offline entitlement container.

This tool:
    1. Builds an Entitle entitlement payload.
    2. Sends it to BrisartSecurityResearch through entitle_bsr_adapter.py.
    3. Saves the protected entitlement envelope to disk.

Example:

    python entitle_issue.py ^
        --issuer JasonBrisart ^
        --subject ResearchLabA ^
        --product EntitleDemo ^
        --entitlement-id lab-a-demo-001 ^
        --master-key "change-this-master-key-change-this-master-key" ^
        --drbg-seed "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa" ^
        --drbg-personalization "EntitleDemoPersonalization" ^
        --output entitlements/lab_a.entitle

Linux/macOS:

    python entitle_issue.py \
        --issuer JasonBrisart \
        --subject ResearchLabA \
        --product EntitleDemo \
        --entitlement-id lab-a-demo-001 \
        --master-key "change-this-master-key-change-this-master-key" \
        --drbg-seed "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa" \
        --drbg-personalization "EntitleDemoPersonalization" \
        --output entitlements/lab_a.entitle
"""

import argparse
import datetime
import json

from entitle_core import make_entitlement_payload
from entitle_bsr_adapter import (
    protect_entitlement_payload,
    save_protected_entitlement,
)


def utc_now_iso():
    return datetime.datetime.now(
        datetime.timezone.utc
    ).replace(microsecond=0).isoformat()


def encode_text(value):
    return value.encode("utf-8")


def build_default_rights(args):
    return {
        "can_run": True,
        "can_use_enterprise_features": args.enterprise,
        "can_modify": args.modify,
        "can_fork": args.fork,
        "can_export_source": args.export_source,
        "can_redistribute": args.redistribute,
        "deployment_limit": args.deployment_limit,
        "support_tier": args.support_tier,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Create a protected Entitle entitlement container."
    )

    parser.add_argument("--issuer", required=True, help="Issuer ID.")
    parser.add_argument("--subject", required=True, help="Customer/lab/organization ID.")
    parser.add_argument("--product", required=True, help="Product ID.")
    parser.add_argument("--entitlement-id", required=True, help="Entitlement ID.")
    parser.add_argument("--expires", default=None, help="Expiration ISO timestamp.")
    parser.add_argument("--output", required=True, help="Output .entitle path.")

    parser.add_argument(
        "--master-key",
        required=True,
        help="BSR master key text. Use strong local key material.",
    )

    parser.add_argument(
        "--drbg-seed",
        required=True,
        help="DRBG seed text. BSR requires sufficient seed material.",
    )

    parser.add_argument(
        "--drbg-personalization",
        required=True,
        help="DRBG personalization text.",
    )

    parser.add_argument(
        "--enterprise",
        action="store_true",
        help="Grant enterprise feature rights.",
    )

    parser.add_argument(
        "--modify",
        action="store_true",
        help="Grant private modification rights.",
    )

    parser.add_argument(
        "--fork",
        action="store_true",
        help="Grant internal fork rights.",
    )

    parser.add_argument(
        "--export-source",
        action="store_true",
        help="Grant source export rights.",
    )

    parser.add_argument(
        "--redistribute",
        action="store_true",
        help="Grant redistribution rights.",
    )

    parser.add_argument(
        "--deployment-limit",
        type=int,
        default=1,
        help="Maximum authorized deployments.",
    )

    parser.add_argument(
        "--support-tier",
        default="standard",
        help="Support tier label.",
    )

    args = parser.parse_args()

    payload = make_entitlement_payload(
        issuer_id=args.issuer,
        subject_id=args.subject,
        product_id=args.product,
        entitlement_id=args.entitlement_id,
        issued_at=utc_now_iso(),
        expires_at=args.expires,
        rights=build_default_rights(args),
        metadata={
            "created_by": "Entitle",
            "protection": "BrisartSecurityResearch envelope",
            "note": "Offline protected entitlement container.",
        },
    )

    envelope = protect_entitlement_payload(
        payload=payload,
        master_key=encode_text(args.master_key),
        drbg_seed=encode_text(args.drbg_seed),
        drbg_personalization=encode_text(args.drbg_personalization),
    )

    save_protected_entitlement(envelope, args.output)

    print("Protected entitlement created:")
    print(args.output)
    print()
    print("Payload summary:")
    print(json.dumps(payload, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()