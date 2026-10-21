import re
from datetime import date
from decimal import Decimal, InvalidOperation


VALID_ACCOUNT_TYPES = {"CHECKING", "SAVINGS", "INVESTMENT"}
VALID_STATUSES = {"ACTIVE", "INACTIVE", "CLOSED"}

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validate_customer(customer):
    errors = []

    customer_id = customer.get("customer_id", "").strip()
    first_name = customer.get("first_name", "").strip()
    last_name = customer.get("last_name", "").strip()
    email = customer.get("email", "").strip()
    created_at = customer.get("created_at", "").strip()

    if not customer_id:
        errors.append("customer_id is required")

    if not first_name:
        errors.append("first_name is required")

    if not last_name:
        errors.append("last_name is required")

    if not email:
        errors.append("email is required")
    elif not EMAIL_PATTERN.fullmatch(email):
        errors.append("email format is invalid")

    if not created_at:
        errors.append("created_at is required")
    else:
        try:
            date.fromisoformat(created_at)
        except ValueError:
            errors.append("created_at must be a valid ISO date")

    return errors


def validate_account(account, valid_customer_ids):
    errors = []

    account_id = account.get("account_id", "").strip()
    customer_id = account.get("customer_id", "").strip()
    account_type = account.get("account_type", "").strip().upper()
    balance_text = account.get("balance", "").strip()
    status = account.get("status", "").strip().upper()

    if not account_id:
        errors.append("account_id is required")

    if not customer_id:
        errors.append("customer_id is required")
    elif customer_id not in valid_customer_ids:
        errors.append("customer_id does not reference a valid customer")

    if account_type not in VALID_ACCOUNT_TYPES:
        errors.append("account_type is invalid")

    try:
        balance = Decimal(balance_text)
        if not balance.is_finite():
            errors.append("balance must be a finite number")
        elif balance < 0:
            errors.append("balance cannot be negative")
    except InvalidOperation:
        errors.append("balance must be numeric")

    if status not in VALID_STATUSES:
        errors.append("status is invalid")

    return errors