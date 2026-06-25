from pathlib import Path

from budget.db import (
    create_transaction,
    delete_transaction,
    initialize_database,
    list_transactions,
    seed_database_from_csv_dir,
    transaction_count,
    update_transaction,
)

DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def test_seed_database_from_all_csv_files(tmp_path: Path) -> None:
    db_path = tmp_path / "budget.sqlite3"
    initialize_database(db_path)

    inserted = seed_database_from_csv_dir(db_path, DATA_DIR)

    assert inserted == 5260
    assert transaction_count(db_path) == 5260


def test_transaction_crud_round_trip(tmp_path: Path) -> None:
    db_path = tmp_path / "budget.sqlite3"
    initialize_database(db_path)

    transaction_id = create_transaction(
        db_path,
        {
            "date": "2026-07-01",
            "type": "지출",
            "category": "식비",
            "description": "테스트 점심",
            "amount": -9000,
            "memo": "등록",
        },
    )
    update_transaction(
        db_path,
        transaction_id,
        {
            "date": "2026-07-02",
            "type": "수입",
            "category": "기타수입",
            "description": "테스트 환급",
            "amount": 15000,
            "memo": "수정",
        },
    )

    transactions = list_transactions(db_path)

    assert transactions[0]["description"] == "테스트 환급"
    assert transactions[0]["amount"] == 15000

    delete_transaction(db_path, transaction_id)

    assert list_transactions(db_path) == []
