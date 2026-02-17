from decimal import Decimal

from fastapi.testclient import TestClient

from app.main import app
from app.db import Base, engine

client = TestClient(app)


def setup_function():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def _create_rate(*, rate_date: str, base_currency: str, quote_currency: str, side: str, rate: str):
    payload = {
        "rate_date": rate_date,
        "base_currency": base_currency,
        "quote_currency": quote_currency,
        "side": side,
        "rate": rate,
    }
    return client.post("/rates", json=payload)


def test_rate_lookup_and_transaction_calc():
    res = _create_rate(
        rate_date="2026-02-02",
        base_currency="PHP",
        quote_currency="USD",
        side="SELL",
        rate="0.017",
    )
    assert res.status_code == 200

    txn_payload = {
        "timestamp": "2026-02-02T10:15:00+08:00",
        "base_currency": "PHP",
        "quote_currency": "USD",
        "side": "SELL",
        "foreign_amount": "1000.00",
    }
    res = client.post("/transactions", json=txn_payload)
    assert res.status_code == 200
    body = res.json()
    assert Decimal(body["effective_rate"]) == Decimal("0.017")
    assert Decimal(body["base_amount"]) > 0


def test_missing_rate_returns_422():
    txn_payload = {
        "timestamp": "2026-02-03T10:15:00+08:00",
        "base_currency": "PHP",
        "quote_currency": "USD",
        "side": "SELL",
        "foreign_amount": "1000.00",
    }
    res = client.post("/transactions", json=txn_payload)
    assert res.status_code == 422


def test_rate_upsert_keeps_single_record_for_composite_key():
    first = _create_rate(
        rate_date="2026-02-10",
        base_currency="USD",
        quote_currency="PHP",
        side="BUY",
        rate="57.1000",
    )
    assert first.status_code == 200

    second = _create_rate(
        rate_date="2026-02-10",
        base_currency="USD",
        quote_currency="PHP",
        side="BUY",
        rate="57.9000",
    )
    assert second.status_code == 200

    res = client.get(
        "/rates",
        params={
            "rate_date": "2026-02-10",
            "base_currency": "USD",
            "quote_currency": "PHP",
            "side": "BUY",
        },
    )
    assert res.status_code == 200
    rates = res.json()
    assert len(rates) == 1
    assert Decimal(rates[0]["rate"]) == Decimal("57.9000")


def test_buy_and_sell_use_different_daily_rates():
    _create_rate(
        rate_date="2026-02-11",
        base_currency="USD",
        quote_currency="PHP",
        side="BUY",
        rate="57.0000",
    )
    _create_rate(
        rate_date="2026-02-11",
        base_currency="USD",
        quote_currency="PHP",
        side="SELL",
        rate="58.5000",
    )

    buy_quote = client.post(
        "/quotes",
        json={
            "timestamp": "2026-02-11T09:00:00+08:00",
            "base_currency": "USD",
            "quote_currency": "PHP",
            "side": "BUY",
            "foreign_amount": "100.00",
        },
    )
    sell_quote = client.post(
        "/quotes",
        json={
            "timestamp": "2026-02-11T09:00:00+08:00",
            "base_currency": "USD",
            "quote_currency": "PHP",
            "side": "SELL",
            "foreign_amount": "100.00",
        },
    )
    assert buy_quote.status_code == 200
    assert sell_quote.status_code == 200
    buy_body = buy_quote.json()
    sell_body = sell_quote.json()
    assert Decimal(buy_body["effective_rate"]) == Decimal("57.0000")
    assert Decimal(sell_body["effective_rate"]) == Decimal("58.5000")
    assert Decimal(buy_body["base_amount"]) != Decimal(sell_body["base_amount"])


def test_quote_rejects_both_amount_fields():
    _create_rate(
        rate_date="2026-02-12",
        base_currency="USD",
        quote_currency="PHP",
        side="BUY",
        rate="57.2500",
    )
    res = client.post(
        "/quotes",
        json={
            "timestamp": "2026-02-12T10:00:00+08:00",
            "base_currency": "USD",
            "quote_currency": "PHP",
            "side": "BUY",
            "foreign_amount": "100.00",
            "base_amount": "1000.00",
        },
    )
    assert res.status_code == 422


def test_quote_confirm_flow_and_prevent_double_confirm():
    _create_rate(
        rate_date="2026-02-13",
        base_currency="USD",
        quote_currency="PHP",
        side="BUY",
        rate="57.2500",
    )
    quote_res = client.post(
        "/quotes",
        json={
            "timestamp": "2026-02-13T10:15:00+08:00",
            "base_currency": "USD",
            "quote_currency": "PHP",
            "side": "BUY",
            "foreign_amount": "100.00",
        },
    )
    assert quote_res.status_code == 200
    quote_id = quote_res.json()["quote_id"]

    confirm_first = client.post("/transactions/confirm", json={"quote_id": quote_id})
    assert confirm_first.status_code == 200

    confirm_second = client.post("/transactions/confirm", json={"quote_id": quote_id})
    assert confirm_second.status_code == 409
