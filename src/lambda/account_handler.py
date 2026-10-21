
import csv
import io
import os
from collections import Counter

import boto3

from validation import validate_account

s3 = boto3.client("s3")
BUCKET_NAME = os.environ["BUCKET_NAME"]


def read_csv(key):
    response = s3.get_object(Bucket=BUCKET_NAME, Key=key)
    content = response["Body"].read().decode("utf-8-sig")
    return list(csv.DictReader(io.StringIO(content)))


def write_csv(key, records, fieldnames):
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(records)

    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=key,
        Body=output.getvalue().encode("utf-8"),
        ContentType="text/csv",
    )


def lambda_handler(event, context):
    accounts = read_csv(event.get("source_key", "raw/accounts.csv"))

    # Only customers accepted by the customer-validation stage are valid.
    valid_customers = read_csv("curated/valid_customers.csv")
    valid_customer_ids = {
        row["customer_id"].strip() for row in valid_customers
    }

    # Reject every account with a duplicated account ID.
    counts = Counter(
        row.get("account_id", "").strip()
        for row in accounts
        if row.get("account_id", "").strip()
    )

    valid_accounts = []
    rejected_accounts = []

    for account in accounts:
        account_id = account.get("account_id", "").strip()
        errors = []

        if account_id and counts[account_id] > 1:
            errors.append("account_id is duplicated")

        errors.extend(validate_account(account, valid_customer_ids))

        if errors:
            rejected_accounts.append({
                **account,
                "validation_errors": "; ".join(errors),
            })
        else:
            valid_accounts.append(account)

    fields = list(accounts[0].keys()) if accounts else []

    write_csv("curated/valid_accounts.csv", valid_accounts, fields)
    write_csv(
        "rejected/rejected_accounts.csv",
        rejected_accounts,
        fields + ["validation_errors"],
    )

    return {
        "status": "SUCCESS",
        "total_records": len(accounts),
        "valid_records": len(valid_accounts),
        "rejected_records": len(rejected_accounts),
    }
