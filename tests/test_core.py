import csv
from pathlib import Path

from budget.core import (
    Transaction,
    add_transaction,
    filter_by_category,
    get_balance,
    load_transactions_from_csv,
    monthly_summary,
)

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


def test_filter_by_category_matches_case_insensitively() -> None:
    transactions: list[Transaction] = [
        {
            "date": "2026-01-01",
            "type": "지출",
            "category": "Food",
            "description": "Lunch",
            "amount": -12000,
            "memo": "",
        },
        {
            "date": "2026-01-02",
            "type": "지출",
            "category": "교통",
            "description": "버스",
            "amount": -1500,
            "memo": "",
        },
    ]

    result = filter_by_category(transactions, "food")

    assert result == [transactions[0]]


def test_filter_by_category_returns_empty_list_for_missing_category() -> None:
    transactions = _load_step2_transactions(limit=3)

    assert filter_by_category(transactions, "없는카테고리") == []


def test_filter_by_category_returns_independent_transactions() -> None:
    transactions = _load_step2_transactions(limit=3)

    result = filter_by_category(transactions, "의료")
    result[0]["memo"] = "changed"

    assert transactions[1]["memo"] == "카드결제"


def test_load_transactions_from_csv_loads_step1_rows() -> None:
    transactions = load_transactions_from_csv(
        DATA_DIR / "step1_transactions.csv"
    )

    assert len(transactions) == 10
    assert transactions[0] == {
        "date": "2026-01-05",
        "type": "지출",
        "category": "식비",
        "description": "점심식사",
        "amount": -12000,
        "memo": "",
    }
    assert transactions[-1] == {
        "date": "2026-01-28",
        "type": "기타수입",
        "category": "기타수입",
        "description": "중고 판매",
        "amount": 25000,
        "memo": "중고마켓",
    }


def test_load_transactions_from_csv_converts_amount_to_int() -> None:
    transactions = load_transactions_from_csv(
        DATA_DIR / "step1_transactions.csv"
    )

    assert isinstance(transactions[0]["amount"], int)


def test_monthly_summary_calculates_income_expense_and_net() -> None:
    transactions: list[Transaction] = [
        {
            "date": "2026-01-05",
            "type": "수입",
            "category": "급여",
            "description": "월급",
            "amount": 3500000,
            "memo": "",
        },
        {
            "date": "2026-01-06",
            "type": "지출",
            "category": "식비",
            "description": "점심",
            "amount": -12000,
            "memo": "",
        },
        {
            "date": "2026-02-01",
            "type": "지출",
            "category": "교통",
            "description": "버스",
            "amount": -1500,
            "memo": "",
        },
    ]

    assert monthly_summary(transactions) == {
        "2026-01": {"income": 3500000, "expense": -12000, "net": 3488000},
        "2026-02": {"income": 0, "expense": -1500, "net": -1500},
    }


def test_monthly_summary_uses_step3_csv_data() -> None:
    transactions = load_transactions_from_csv(
        DATA_DIR / "step3_transactions.csv"
    )
    summary = monthly_summary(transactions)

    assert summary["2025-01"] == {
        "income": 405037,
        "expense": -2886860,
        "net": -2481823,
    }


def test_large_transactions_csv_loads_5000_rows() -> None:
    transactions = load_transactions_from_csv(
        DATA_DIR / "step4_large_transactions.csv"
    )

    assert len(transactions) == 5000


def test_large_transactions_balance_is_correct() -> None:
    transactions = load_transactions_from_csv(
        DATA_DIR / "step4_large_transactions.csv"
    )

    assert get_balance(transactions) == 1134968783.0


def test_large_transactions_monthly_summary_has_65_or_more_months() -> None:
    transactions = load_transactions_from_csv(
        DATA_DIR / "step4_large_transactions.csv"
    )
    summary = monthly_summary(transactions)

    assert len(summary) >= 65
    assert min(summary) == "2020-01"
    assert max(summary) == "2026-06"
