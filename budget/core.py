"""Core budget transaction functions."""

import csv
from pathlib import Path

Transaction = dict[str, str | int | float]
MonthlySummary = dict[str, dict[str, int]]


def add_transaction(
    transactions: list[Transaction],
    transaction: Transaction,
) -> list[Transaction]:
    """Return transactions with a new transaction added."""
    return [*transactions, transaction]


def get_balance(transactions: list[Transaction]) -> float:
    """Return the sum of all transaction amounts."""
    return float(
        sum(float(transaction["amount"]) for transaction in transactions)
    )


def filter_by_category(
    transactions: list[Transaction],
    category: str,
) -> list[Transaction]:
    """Return transactions that match the given category."""
    normalized_category = category.casefold()
    return [
        dict(transaction)
        for transaction in transactions
        if str(transaction["category"]).casefold() == normalized_category
    ]


def load_transactions_from_csv(file_path: str | Path) -> list[Transaction]:
    """Load transactions from a CSV file."""
    transactions: list[Transaction] = []

    with Path(file_path).open(encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
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


def monthly_summary(transactions: list[Transaction]) -> MonthlySummary:
    """Return monthly income, expense, and net totals."""
    summary: MonthlySummary = {}

    for transaction in transactions:
        month = str(transaction["date"])[:7]
        amount = int(transaction["amount"])

        if month not in summary:
            summary[month] = {"income": 0, "expense": 0, "net": 0}

        if amount > 0:
            summary[month]["income"] += amount
        else:
            summary[month]["expense"] += amount

        summary[month]["net"] += amount

    return summary
