import csv
import json
from pathlib import Path

from src.validation import validate_account, validate_customer


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = PROJECT_ROOT / "data" / "source"
OUTPUT_DIR = PROJECT_ROOT / "data" / "output"


def read_csv(filename):
    path = SOURCE_DIR / filename

    with path.open("r", newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def write_csv(path, fieldnames, rows):
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_rejected_csv(path, original_fields, rejected_records):
    fieldnames = original_fields + ["errors"]
    rows = []

    for item in rejected_records:
        row = dict(item["record"])
        row["errors"] = "; ".join(item["errors"])
        rows.append(row)

    write_csv(path, fieldnames, rows)


def find_duplicates(records, id_field):
    seen = set()
    duplicates = set()

    for record in records:
        record_id = record.get(id_field, "").strip()

        if record_id in seen:
            duplicates.add(record_id)
        else:
            seen.add(record_id)

    return duplicates


def process_customers(customers):
    duplicate_ids = find_duplicates(customers, "customer_id")
    valid_customers = []
    rejected_customers = []

    for customer in customers:
        errors = validate_customer(customer)
        customer_id = customer.get("customer_id", "").strip()

        if customer_id in duplicate_ids:
            errors.append("customer_id is duplicated")

        if errors:
            rejected_customers.append({
                "record": customer,
                "errors": errors,
            })
        else:
            valid_customers.append(customer)

    return valid_customers, rejected_customers


def process_accounts(accounts, valid_customer_ids):
    duplicate_ids = find_duplicates(accounts, "account_id")
    valid_accounts = []
    rejected_accounts = []

    for account in accounts:
        errors = validate_account(account, valid_customer_ids)
        account_id = account.get("account_id", "").strip()

        if account_id in duplicate_ids:
            errors.append("account_id is duplicated")

        if errors:
            rejected_accounts.append({
                "record": account,
                "errors": errors,
            })
        else:
            valid_accounts.append(account)

    return valid_accounts, rejected_accounts


def run_pipeline():
    customers = read_csv("customers.csv")
    accounts = read_csv("accounts.csv")

    valid_customers, rejected_customers = process_customers(customers)

    valid_customer_ids = {
        customer["customer_id"].strip()
        for customer in valid_customers
    }

    valid_accounts, rejected_accounts = process_accounts(
        accounts,
        valid_customer_ids,
    )

    customer_fields = list(customers[0].keys()) if customers else []
    account_fields = list(accounts[0].keys()) if accounts else []

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    write_csv(
        OUTPUT_DIR / "valid_customers.csv",
        customer_fields,
        valid_customers,
    )
    write_rejected_csv(
        OUTPUT_DIR / "rejected_customers.csv",
        customer_fields,
        rejected_customers,
    )
    write_csv(
        OUTPUT_DIR / "valid_accounts.csv",
        account_fields,
        valid_accounts,
    )
    write_rejected_csv(
        OUTPUT_DIR / "rejected_accounts.csv",
        account_fields,
        rejected_accounts,
    )

    report = {
        "customers": {
            "source_count": len(customers),
            "valid_count": len(valid_customers),
            "rejected_count": len(rejected_customers),
            "reconciled": (
                len(customers)
                == len(valid_customers) + len(rejected_customers)
            ),
        },
        "accounts": {
            "source_count": len(accounts),
            "valid_count": len(valid_accounts),
            "rejected_count": len(rejected_accounts),
            "reconciled": (
                len(accounts)
                == len(valid_accounts) + len(rejected_accounts)
            ),
        },
    }

    with (OUTPUT_DIR / "reconciliation.json").open(
        "w", encoding="utf-8"
    ) as file:
        json.dump(report, file, indent=2)

    print("=== Migration Validation Summary ===")
    print(f"Customers: {len(customers)} source, "
          f"{len(valid_customers)} valid, "
          f"{len(rejected_customers)} rejected")
    print(f"Accounts: {len(accounts)} source, "
          f"{len(valid_accounts)} valid, "
          f"{len(rejected_accounts)} rejected")
    print(f"Customer counts reconciled: "
          f"{report['customers']['reconciled']}")
    print(f"Account counts reconciled: "
          f"{report['accounts']['reconciled']}")
    print(f"Output directory: {OUTPUT_DIR}")

    return report


if __name__ == "__main__":
    run_pipeline()