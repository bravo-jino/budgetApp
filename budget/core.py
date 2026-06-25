"""Core budget transaction functions."""

from pathlib import Path

Transaction = dict[str, str | int | float]
MonthlySummary = dict[str, dict[str, int]]


def add_transaction(
    transactions: list[Transaction],
    transaction: Transaction,
) -> list[Transaction]:
    """Return transactions with a new transaction added."""
    pass


def get_balance(transactions: list[Transaction]) -> float:
    """Return the sum of all transaction amounts."""
    return float(sum(float(transaction["amount"]) for transaction in transactions))


def filter_by_category(
    transactions: list[Transaction],
    category: str,
) -> list[Transaction]:
    """Return transactions that match the given category."""
    pass


def load_transactions_from_csv(file_path: str | Path) -> list[Transaction]:
    """Load transactions from a CSV file."""
    pass


def monthly_summary(transactions: list[Transaction]) -> MonthlySummary:
    """Return monthly income, expense, and net totals."""
    pass
