from pathlib import Path

from flask import Flask

from budget.web import create_app

DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def test_create_app_returns_flask_app() -> None:
    app = create_app()

    assert isinstance(app, Flask)


def test_index_renders_database_dashboard(tmp_path: Path) -> None:
    app = create_app(data_dir=DATA_DIR, db_path=tmp_path / "budget.sqlite3")

    response = app.test_client().get("/")

    assert response.status_code == 200
    assert "통합 DB 가계부" in response.text
    assert "항목별 통계" in response.text
    assert "월별 항목별 비중" in response.text
    assert "5260" in response.text


def test_web_app_can_create_update_and_delete_transaction(
    tmp_path: Path,
) -> None:
    app = create_app(data_dir=DATA_DIR, db_path=tmp_path / "budget.sqlite3")
    client = app.test_client()

    create_response = client.post(
        "/transactions",
        data={
            "date": "2026-07-01",
            "type": "지출",
            "category": "식비",
            "description": "웹 등록",
            "amount": "-12000",
            "memo": "폼",
        },
        follow_redirects=True,
    )

    assert create_response.status_code == 200
    assert "웹 등록" in create_response.text

    edit_page = client.get("/")
    marker = 'data-edit-id="'
    transaction_id = edit_page.text.split(marker, 1)[1].split('"', 1)[0]
    update_response = client.post(
        f"/transactions/{transaction_id}/update",
        data={
            "date": "2026-07-02",
            "type": "수입",
            "category": "기타수입",
            "description": "웹 수정",
            "amount": "25000",
            "memo": "수정",
        },
        follow_redirects=True,
    )

    assert "웹 수정" in update_response.text

    delete_response = client.post(
        f"/transactions/{transaction_id}/delete",
        follow_redirects=True,
    )

    assert "웹 수정" not in delete_response.text
