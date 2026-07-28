"""
Entitle Verify Tool

Verifies a protected Entitle entitlement container.

Example:

    python entitle_verify.py ^
        --issuer JasonBrisart ^
        --subject ResearchLabA ^
        --product EntitleDemo ^
        --master-key "change-this-master-key-change-this-master-key" ^
        --file entitlements/lab_a.entitle
"""

import argparse
import json

from entitle_bsr_adapter import verify_protected_entitlement


def encode_text(value):
    return value.encode("utf-8")


def main():
    parser = argparse.ArgumentParser(
        description="Verify a protected Entitle entitlement container."
    )

    parser.add_argument("--issuer", required=True, help="Expected issuer ID.")
    parser.add_argument("--subject", required=True, help="Expected subject/customer/lab ID.")
    parser.add_argument("--product", required=True, help="Expected product ID.")
    parser.add_argument("--master-key", required=True, help="BSR master key text.")
    parser.add_argument("--file", required=True, help="Protected .entitle file.")

    args = parser.parse_args()

    result = verify_protected_entitlement(
        path=args.file,
        master_key=encode_text(args.master_key),
        expected_product_id=args.product,
        issuer_id=args.issuer,
        subject_id=args.subject,
    )

    print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))

    if result.allowed:
        print()
        print("VERIFIED: entitlement is valid.")
    else:
        print()
        print(f"DENIED: {result.reason}")


if __name__ == "__main__":
    main()