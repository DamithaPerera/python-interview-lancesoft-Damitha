from datetime import datetime, timedelta
from decimal import Decimal

from fastapi.testclient import TestClient

from app.db import Base, SessionLocal, engine
from app.main import app
from app.repositories import quote_repository

client = TestClient(app)


def setup_function():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def _create_rate(*, rate_date: str, base_currency: str, quote_currency: str, side: str, rate: str):
    return client.post(
        "/rates",
        json={
            "rate_date": rate_date,
            "base_currency": base_currency,
            "quote_currency": quote_currency,
            "side": side,
            "rate": rate,
        },
    )


def _create_quote():
    _create_rate(
        rate_date="2026-04-01",
        base_currency="USD",
        quote_currency="PHP",
        side="BUY",
        rate="57.2500",
    )
    res = client.post(
        "/quotes",
        json={
            "timestamp": "2026-04-01T10:00:00+08:00",
            "base_currency": "USD",
            "quote_currency": "PHP",
            "side": "BUY",
            "foreign_amount": "100.00",
        },
    )
    assert res.status_code == 200
    return res.json()


def test_post_rates_and_get_rates_list():
    res = _create_rate(
        rate_date="2026-03-20",
        base_currency="usd",
        quote_currency="php",
        side="buy",
        rate="57.0000",
    )
    assert res.status_code == 200
    body = res.json()
    assert body["base_currency"] == "USD"
    assert body["quote_currency"] == "PHP"
    assert body["side"] == "BUY"

    list_res = client.get(
        "/rates",
        params={
            "rate_date": "2026-03-20",
            "base_currency": "USD",
            "quote_currency": "PHP",
            "side": "BUY",
        },
    )
    assert list_res.status_code == 200
    items = list_res.json()
    assert len(items) == 1
    assert Decimal(items[0]["rate"]) == Decimal("57.0000")


def test_get_put_delete_rates_key_routes():
    _create_rate(
        rate_date="2026-03-21",
        base_currency="USD",
        quote_currency="PHP",
        side="SELL",
        rate="58.1000",
    )

    get_res = client.get("/rates/2026-03-21/USD/PHP/SELL")
    assert get_res.status_code == 200

    put_res = client.put("/rates/2026-03-21/USD/PHP/SELL", json={"rate": "58.9000"})
    assert put_res.status_code == 200
    assert Decimal(put_res.json()["rate"]) == Decimal("58.9000")

    del_res = client.delete("/rates/2026-03-21/USD/PHP/SELL")
    assert del_res.status_code == 200
    assert del_res.json() == {"deleted": True}

    get_missing = client.get("/rates/2026-03-21/USD/PHP/SELL")
    assert get_missing.status_code == 404


def test_rates_key_routes_not_found():
    assert client.get("/rates/2026-03-22/USD/PHP/BUY").status_code == 404
    assert client.put("/rates/2026-03-22/USD/PHP/BUY", json={"rate": "57.1000"}).status_code == 404
    assert client.delete("/rates/2026-03-22/USD/PHP/BUY").status_code == 404


def test_post_quotes_success_and_validation_errors():
    _create_rate(
        rate_date="2026-03-23",
        base_currency="USD",
        quote_currency="PHP",
        side="BUY",
        rate="57.2500",
    )
    ok = client.post(
        "/quotes",
        json={
            "timestamp": "2026-03-23T10:00:00+08:00",
            "base_currency": "USD",
            "quote_currency": "PHP",
            "side": "BUY",
            "foreign_amount": "100.00",
        },
    )
    assert ok.status_code == 200
    quote = ok.json()
    assert quote["quote_id"].startswith("QTE-")
    assert quote["confirmed"] is False

    invalid = client.post(
        "/quotes",
        json={
            "timestamp": "2026-03-23T10:00:00+08:00",
            "base_currency": "USD",
            "quote_currency": "PHP",
            "side": "BUY",
            "foreign_amount": "100.00",
            "base_amount": "1000.00",
        },
    )
    assert invalid.status_code == 422

    missing_rate = client.post(
        "/quotes",
        json={
            "timestamp": "2026-03-24T10:00:00+08:00",
            "base_currency": "USD",
            "quote_currency": "PHP",
            "side": "BUY",
            "foreign_amount": "100.00",
        },
    )
    assert missing_rate.status_code == 422


def test_post_transactions_success_and_missing_rate_422():
    _create_rate(
        rate_date="2026-03-25",
        base_currency="USD",
        quote_currency="PHP",
        side="SELL",
        rate="58.2500",
    )
    ok = client.post(
        "/transactions",
        json={
            "timestamp": "2026-03-25T11:00:00+08:00",
            "base_currency": "USD",
            "quote_currency": "PHP",
            "side": "SELL",
            "foreign_amount": "100.00",
        },
    )
    assert ok.status_code == 200
    assert ok.json()["transaction_id"].startswith("TXN-")

    missing = client.post(
        "/transactions",
        json={
            "timestamp": "2026-03-26T11:00:00+08:00",
            "base_currency": "USD",
            "quote_currency": "PHP",
            "side": "SELL",
            "foreign_amount": "100.00",
        },
    )
    assert missing.status_code == 422


def test_post_transactions_confirm_success_conflict_not_found_and_expired():
    quote = _create_quote()
    quote_id = quote["quote_id"]

    confirm_ok = client.post("/transactions/confirm", json={"quote_id": quote_id})
    assert confirm_ok.status_code == 200

    confirm_again = client.post("/transactions/confirm", json={"quote_id": quote_id})
    assert confirm_again.status_code == 409

    confirm_missing = client.post("/transactions/confirm", json={"quote_id": "QTE-DOES-NOT-EXIST"})
    assert confirm_missing.status_code == 404

    quote_2 = _create_quote()
    quote_2_id = quote_2["quote_id"]
    db = SessionLocal()
    try:
        q = quote_repository.get_by_quote_id(db, quote_id=quote_2_id)
        q.expires_at = datetime.utcnow() - timedelta(minutes=1)
        db.add(q)
        db.commit()
    finally:
        db.close()

    confirm_expired = client.post("/transactions/confirm", json={"quote_id": quote_2_id})
    assert confirm_expired.status_code == 422
