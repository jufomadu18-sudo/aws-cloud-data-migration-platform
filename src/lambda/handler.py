
import csv
import io
import os
from collections import Counter

import boto3

from validation import validate_customer

s3 = boto3.client("s3")

BUCKET_NAME = os.environ["BUCKET_NAME"]


def read_csv_from_s3(key):
    response = s3.get_object(Bucket=BUCKET_NAME, Key=key)
    content = response["Body"].read().decode("utf-8-sig")
    return list(csv.DictReader(io.StringIO(content)))


def write_csv_to_s3(key, records, fieldnames):
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
    source_key = event.get("source_key", "raw/customers.csv")
    customers = read_csv_from_s3(source_key)

    # Find duplicate IDs before validating individual records.
    id_counts = Counter(
        row.get("customer_id", "").strip()
        for row in customers
        if row.get("customer_id", "").strip()
    )

    valid_customers = []
    rejected_customers = []

    for customer in customers:
        customer_id = customer.get("customer_id", "").strip()
        errors = []

        if customer_id and id_counts[customer_id] > 1:
            errors.append("customer_id is duplicated")

        errors.extend(validate_customer(customer))

        if errors:
            rejected_customers.append({
                **customer,
                "validation_errors": "; ".join(errors),
            })
        else:
            valid_customers.append(customer)

    source_fields = list(customers[0].keys()) if customers else []
    rejected_fields = source_fields + ["validation_errors"]

    write_csv_to_s3(
        "curated/valid_customers.csv",
        valid_customers,
        source_fields,
    )

    write_csv_to_s3(
        "rejected/rejected_customers.csv",
        rejected_customers,
        rejected_fields,
    )

    return {
        "status": "SUCCESS",
        "source_key": source_key,
        "total_records": len(customers),
        "valid_records": len(valid_customers),
        "rejected_records": len(rejected_customers),
    }
