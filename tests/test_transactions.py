from datetime import datetime
from decimal import Decimal

from fastapi.testclient import TestClient

from main import app
from db import Base, engine

client = TestClient(app)


def setup_module():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def test_rate_lookup_and_transaction_calc():
    payload = {
        "rate_date": "2026-02-02",
        "base_currency": "PHP",
        "quote_currency": "USD",
        "side": "SELL",
        "rate": "0.017",
    }
    res = client.post("/rates", json=payload)
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
    assert body["effective_rate"] == "0.017"
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