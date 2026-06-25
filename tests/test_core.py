import csv
from pathlib import Path

from budget.core import Transaction, add_transaction, get_balance

DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def _load_step2_transactions(limit: int) -> list[Transaction]:
    transactions: list[Transaction] = []
    csv_path = DATA_DIR / "step2_transactions.csv"

    with csv_path.open(encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        for index, row in enumerate(reader):
            if index == limit:
                break
            transactions.append(
                {
                    "date": row["date"],
                    "type": row["type"],
                    "category": row["category"],
                    "description": row["description"],
                    "amount": int(row["amount"]),
                    "memo": row["memo"],
                }
            )

    return transactions


def test_add_transaction_increases_length() -> None:
    transactions: list[Transaction] = []
    transaction: Transaction = {
        "date": "2026-01-05",
        "type": "지출",
        "category": "식비",
        "description": "점심식사",
        "amount": -12000,
        "memo": "",
    }

    result = add_transaction(transactions, transaction)

    assert len(result) == 1


def test_get_balance_returns_zero_for_empty_transactions() -> None:
    assert get_balance([]) == 0.0


def test_get_balance_sums_income_and_expense_amounts() -> None:
    transactions: list[Transaction] = [
        {
            "date": "2026-01-01",
            "type": "수입",
            "category": "급여",
            "description": "월급",
            "amount": 3000000,
            "memo": "",
        },
        {
            "date": "2026-01-02",
            "type": "지출",
            "category": "식비",
            "description": "점심",
            "amount": -12000,
            "memo": "",
        },
        {
            "date": "2026-01-03",
            "type": "지출",
            "category": "교통",
            "description": "지하철",
            "amount": -1500,
            "memo": "",
        },
    ]

    assert get_balance(transactions) == 2986500.0


def test_get_balance_with_step2_csv_sample() -> None:
    transactions = _load_step2_transactions(limit=11)

    assert get_balance(transactions) == -2939245.0
