from src.pipeline import (
    process_accounts,
    process_customers,
    read_csv,
)


def test_customer_records_reconcile():
    customers = read_csv("customers.csv")

    valid, rejected = process_customers(customers)

    assert len(customers) == len(valid) + len(rejected)


def test_account_records_reconcile():
    customers = read_csv("customers.csv")
    accounts = read_csv("accounts.csv")

    valid_customers, _ = process_customers(customers)
    valid_customer_ids = {
        customer["customer_id"] for customer in valid_customers
    }

    valid, rejected = process_accounts(accounts, valid_customer_ids)

    assert len(accounts) == len(valid) + len(rejected)


def test_rejected_records_have_reasons():
    customers = read_csv("customers.csv")
    accounts = read_csv("accounts.csv")

    _, rejected_customers = process_customers(customers)

    valid_customers, _ = process_customers(customers)
    valid_customer_ids = {
        customer["customer_id"] for customer in valid_customers
    }

    _, rejected_accounts = process_accounts(accounts, valid_customer_ids)

    assert rejected_customers
    assert rejected_accounts
    assert all(item["errors"] for item in rejected_customers)
    assert all(item["errors"] for item in rejected_accounts)