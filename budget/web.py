"""Web application for browsing and editing budget transactions."""

from pathlib import Path

from flask import Flask, redirect, render_template, request, url_for
from flask.typing import ResponseReturnValue

from budget.core import Transaction
from budget.db import (
    category_stats,
    create_transaction,
    delete_transaction,
    initialize_database,
    list_transactions,
    monthly_category_shares,
    monthly_stats,
    seed_database_from_csv_dir,
    transaction_count,
    update_transaction,
)

Dashboard = dict[str, object]


def create_app(
    data_dir: Path | None = None,
    db_path: Path | None = None,
) -> Flask:
    """Create and configure the Flask budget web app."""
    app = Flask(__name__)
    source_dir = data_dir or Path(__file__).resolve().parents[1] / "data"
    database_path = db_path or Path("budget.sqlite3")
    initialize_database(database_path)
    seed_database_from_csv_dir(database_path, source_dir)

    @app.get("/")
    def index() -> str:
        dashboard = _build_dashboard(database_path, request.args.get("month"))
        return render_template(
            "index.html",
            dashboard=dashboard,
        )

    @app.post("/transactions")
    def create() -> ResponseReturnValue:
        create_transaction(database_path, _form_transaction())
        return redirect(url_for("index"))

    @app.post("/transactions/<int:transaction_id>/update")
    def update(transaction_id: int) -> ResponseReturnValue:
        update_transaction(database_path, transaction_id, _form_transaction())
        return redirect(url_for("index"))

    @app.post("/transactions/<int:transaction_id>/delete")
    def delete(transaction_id: int) -> ResponseReturnValue:
        delete_transaction(database_path, transaction_id)
        return redirect(url_for("index"))

    return app


def _build_dashboard(db_path: Path, selected_month: str | None) -> Dashboard:
    """Build display data from the SQLite database."""
    months = monthly_stats(db_path)
    month = selected_month or _first_month(months)
    return {
        "categories": category_stats(db_path),
        "monthly_shares": monthly_category_shares(db_path, month),
        "months": months,
        "selected_month": month,
        "transactions": list_transactions(db_path),
        "transaction_count": transaction_count(db_path),
        "total_balance": _format_won(_sum_net(months)),
    }


def _form_transaction() -> Transaction:
    """Build a transaction from submitted form data."""
    return {
        "date": request.form["date"],
        "type": request.form["type"],
        "category": request.form["category"],
        "description": request.form["description"],
        "amount": int(request.form["amount"]),
        "memo": request.form.get("memo", ""),
    }


def _first_month(months: list[dict[str, object]]) -> str:
    """Return the newest month in the dashboard."""
    return str(months[0]["month"]) if months else ""


def _sum_net(months: list[dict[str, object]]) -> int:
    """Return total net amount across all monthly rows."""
    return sum(int(month["net"]) for month in months)


def _format_won(amount: float | int) -> str:
    """Format a numeric amount for display."""
    return f"{int(amount):,}"


if __name__ == "__main__":  # pragma: no cover
    create_app().run(debug=True)
