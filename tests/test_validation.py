from src.validation import validate_customer, validate_account


def test_valid_customer_passes():
    customer = {
        "customer_id": "C0001",
        "first_name": "Alex",
        "last_name": "Smith001",
        "email": "alex@example.com",
        "created_at": "2024-01-15",
    }

    assert validate_customer(customer) == []


def test_missing_customer_email_fails():
    customer = {
        "customer_id": "C0001",
        "first_name": "Alex",
        "last_name": "Smith001",
        "email": "",
        "created_at": "2024-01-15",
    }

    errors = validate_customer(customer)

    assert "email is required" in errors


def test_invalid_email_fails():
    customer = {
        "customer_id": "C0001",
        "first_name": "Alex",
        "last_name": "Smith001",
        "email": "not-an-email",
        "created_at": "2024-01-15",
    }

    errors = validate_customer(customer)

    assert "email format is invalid" in errors


def test_invalid_date_fails():
    customer = {
        "customer_id": "C0001",
        "first_name": "Alex",
        "last_name": "Smith001",
        "email": "alex@example.com",
        "created_at": "not-a-date",
    }

    errors = validate_customer(customer)

    assert "created_at must be a valid ISO date" in errors


def test_valid_account_passes():
    account = {
        "account_id": "A0001",
        "customer_id": "C0001",
        "account_type": "CHECKING",
        "balance": "125.50",
        "status": "ACTIVE",
    }

    errors = validate_account(account, {"C0001"})

    assert errors == []


def test_negative_balance_fails():
    account = {
        "account_id": "A0001",
        "customer_id": "C0001",
        "account_type": "CHECKING",
        "balance": "-25.00",
        "status": "ACTIVE",
    }

    errors = validate_account(account, {"C0001"})

    assert "balance cannot be negative" in errors


def test_invalid_account_type_fails():
    account = {
        "account_id": "A0001",
        "customer_id": "C0001",
        "account_type": "UNKNOWN",
        "balance": "125.50",
        "status": "ACTIVE",
    }

    errors = validate_account(account, {"C0001"})

    assert "account_type is invalid" in errors


def test_invalid_customer_reference_fails():
    account = {
        "account_id": "A0001",
        "customer_id": "C9999",
        "account_type": "CHECKING",
        "balance": "125.50",
        "status": "ACTIVE",
    }

    errors = validate_account(account, {"C0001"})

    assert "customer_id does not reference a valid customer" in errors