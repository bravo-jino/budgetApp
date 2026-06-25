"""SQLite storage for budget transactions."""

import sqlite3
from pathlib import Path

from budget.core import Transaction, load_transactions_from_csv

DbRow = dict[str, str | int | float]


def initialize_database(db_path: str | Path) -> None:
    """Create the transaction table when it does not exist."""
    with _connect(db_path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                type TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT NOT NULL,
                amount INTEGER NOT NULL,
                memo TEXT NOT NULL DEFAULT '',
                source_file TEXT NOT NULL DEFAULT ''
            )
            """
        )


def seed_database_from_csv_dir(db_path: str | Path, data_dir: Path) -> int:
    """Seed an empty database with every CSV file in the data directory."""
    if transaction_count(db_path) > 0:
        return 0

    inserted = 0
    for csv_path in sorted(data_dir.glob("*.csv")):
        for transaction in load_transactions_from_csv(csv_path):
            create_transaction(db_path, transaction, csv_path.name)
            inserted += 1

    return inserted


def transaction_count(db_path: str | Path) -> int:
    """Return the number of stored transactions."""
    with _connect(db_path) as connection:
        row = connection.execute(
            "SELECT COUNT(*) AS count FROM transactions"
        ).fetchone()
    return int(row["count"])


def list_transactions(db_path: str | Path, limit: int = 300) -> list[DbRow]:
    """Return recent transactions for display."""
    with _connect(db_path) as connection:
        rows = connection.execute(
            """
            SELECT id, date, type, category, description, amount, memo
            FROM transactions
            ORDER BY date DESC, id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [_row_to_dict(row) for row in rows]


def create_transaction(
    db_path: str | Path,
    transaction: Transaction,
    source_file: str = "manual",
) -> int:
    """Insert a transaction and return its id."""
    with _connect(db_path) as connection:
        cursor = connection.execute(
            """
            INSERT INTO transactions
                (date, type, category, description, amount, memo, source_file)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            _transaction_values(transaction, source_file),
        )
    return int(cursor.lastrowid)


def update_transaction(
    db_path: str | Path,
    transaction_id: int,
    transaction: Transaction,
) -> None:
    """Update an existing transaction."""
    values = _transaction_values(transaction, "manual")[:-1]
    with _connect(db_path) as connection:
        connection.execute(
            """
            UPDATE transactions
            SET date = ?, type = ?, category = ?, description = ?,
                amount = ?, memo = ?
            WHERE id = ?
            """,
            (*values, transaction_id),
        )


def delete_transaction(db_path: str | Path, transaction_id: int) -> None:
    """Delete a transaction."""
    with _connect(db_path) as connection:
        connection.execute(
            "DELETE FROM transactions WHERE id = ?",
            (transaction_id,),
        )


def monthly_stats(db_path: str | Path) -> list[DbRow]:
    """Return income, expense, and net totals grouped by month."""
    query = """
        SELECT substr(date, 1, 7) AS month,
               SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) AS income,
               SUM(CASE WHEN amount < 0 THEN amount ELSE 0 END) AS expense,
               SUM(amount) AS net
        FROM transactions
        GROUP BY month
        ORDER BY month DESC
    """
    return _query_rows(db_path, query)


def category_stats(db_path: str | Path) -> list[DbRow]:
    """Return totals grouped by category."""
    query = """
        SELECT category,
               COUNT(*) AS count,
               SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) AS income,
               SUM(CASE WHEN amount < 0 THEN amount ELSE 0 END) AS expense,
               SUM(amount) AS net
        FROM transactions
        GROUP BY category
        ORDER BY ABS(net) DESC
    """
    return _query_rows(db_path, query)


def monthly_category_shares(db_path: str | Path, month: str) -> list[DbRow]:
    """Return expense share by category for one month."""
    query = """
        SELECT category,
               SUM(amount) AS expense,
               ROUND(ABS(SUM(amount)) * 100.0 / ?, 1) AS share
        FROM transactions
        WHERE substr(date, 1, 7) = ? AND amount < 0
        GROUP BY category
        ORDER BY ABS(expense) DESC
    """
    total = _monthly_expense_total(db_path, month)
    return _query_rows(db_path, query, (total, month)) if total else []


def _connect(db_path: str | Path) -> sqlite3.Connection:
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    return connection


def _row_to_dict(row: sqlite3.Row) -> DbRow:
    return dict(row)


def _query_rows(
    db_path: str | Path,
    query: str,
    params: tuple[object, ...] = (),
) -> list[DbRow]:
    with _connect(db_path) as connection:
        rows = connection.execute(query, params).fetchall()
    return [_row_to_dict(row) for row in rows]


def _monthly_expense_total(db_path: str | Path, month: str) -> int:
    query = """
        SELECT ABS(SUM(amount)) AS total
        FROM transactions
        WHERE substr(date, 1, 7) = ? AND amount < 0
    """
    with _connect(db_path) as connection:
        row = connection.execute(query, (month,)).fetchone()
    return int(row["total"] or 0)


def _transaction_values(
    transaction: Transaction,
    source_file: str,
) -> tuple[str, str, str, str, int, str, str]:
    return (
        str(transaction["date"]),
        str(transaction["type"]),
        str(transaction["category"]),
        str(transaction["description"]),
        int(transaction["amount"]),
        str(transaction["memo"]),
        source_file,
    )
