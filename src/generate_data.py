
import csv
import random
from datetime import date, timedelta
from pathlib import Path

SEED = 42
CUSTOMER_COUNT = 100
ACCOUNT_COUNT = 150

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = PROJECT_ROOT / "data" / "source"

random.seed(SEED)

FIRST_NAMES = [
    "Alex", "Jordan", "Taylor", "Morgan", "Casey",
    "Riley", "Jamie", "Cameron", "Avery", "Drew",
]

LAST_NAMES = [
    "Smith", "Johnson", "Brown", "Davis", "Wilson",
    "Miller", "Moore", "Taylor", "Anderson", "Thomas",
]

ACCOUNT_TYPES = ["CHECKING", "SAVINGS", "INVESTMENT"]
STATUSES = ["ACTIVE", "INACTIVE", "CLOSED"]


def write_csv(path, fieldnames, rows):
    """Write rows to a CSV file using a consistent column order."""
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def generate_customers():
    customers = []

    for number in range(1, CUSTOMER_COUNT + 1):
        first_name = FIRST_NAMES[(number - 1) % len(FIRST_NAMES)]
        last_name = LAST_NAMES[(number - 1) % len(LAST_NAMES)]

        customers.append({
            "customer_id": f"C{number:04d}",
            "first_name": first_name,
            "last_name": f"{last_name}{number:03d}",
            "email": f"customer{number:03d}@example.com",
            "created_at": (
                date(2022, 1, 1) + timedelta(days=number * 7)
            ).isoformat(),
        })

    # Deliberately introduce data-quality defects.
    customers[4]["email"] = ""
    customers[9]["email"] = "not-an-email"
    customers[14]["customer_id"] = customers[13]["customer_id"]

    return customers


def generate_accounts():
    accounts = []

    for number in range(1, ACCOUNT_COUNT + 1):
        customer_number = ((number - 1) % CUSTOMER_COUNT) + 1
        balance_cents = random.randint(0, 2_000_000)

        accounts.append({
            "account_id": f"A{number:04d}",
            "customer_id": f"C{customer_number:04d}",
            "account_type": ACCOUNT_TYPES[(number - 1) % len(ACCOUNT_TYPES)],
            "balance": f"{balance_cents / 100:.2f}",
            "status": STATUSES[(number - 1) % len(STATUSES)],
        })

    # Deliberately introduce data-quality defects.
    accounts[2]["balance"] = "-25.00"
    accounts[7]["account_type"] = "UNKNOWN"
    accounts[11]["customer_id"] = "C9999"
    accounts[18]["status"] = "PENDING_REVIEW"

    return accounts


def main():
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)

    customers = generate_customers()
    accounts = generate_accounts()

    write_csv(
        SOURCE_DIR / "customers.csv",
        ["customer_id", "first_name", "last_name", "email", "created_at"],
        customers,
    )

    write_csv(
        SOURCE_DIR / "accounts.csv",
        ["account_id", "customer_id", "account_type", "balance", "status"],
        accounts,
    )

    print("Synthetic source data generated successfully.")
    print(f"Customers: {len(customers)}")
    print(f"Accounts: {len(accounts)}")
    print(f"Output directory: {SOURCE_DIR}")


if __name__ == "__main__":
    main()
