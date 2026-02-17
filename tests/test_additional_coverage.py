from datetime import datetime, timedelta
from decimal import Decimal

from fastapi.testclient import TestClient

from app.core.config import QUOTE_TTL_MINUTES
from app.db import Base, SessionLocal, engine
from app.main import app
from app.repositories import quote_repository, rate_repository
from app.services import get_calculator

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


def test_rate_key_routes_get_put_delete_and_404():
    res = _create_rate(
        rate_date="2026-03-01",
        base_currency="USD",
        quote_currency="PHP",
        side="BUY",
        rate="56.5000",
    )
    assert res.status_code == 200

    get_res = client.get("/rates/2026-03-01/USD/PHP/BUY")
    assert get_res.status_code == 200
    assert Decimal(get_res.json()["rate"]) == Decimal("56.5000")

    put_res = client.put("/rates/2026-03-01/USD/PHP/BUY", json={"rate": "57.0000"})
    assert put_res.status_code == 200
    assert Decimal(put_res.json()["rate"]) == Decimal("57.0000")

    del_res = client.delete("/rates/2026-03-01/USD/PHP/BUY")
    assert del_res.status_code == 200
    assert del_res.json()["deleted"] is True

    missing_res = client.get("/rates/2026-03-01/USD/PHP/BUY")
    assert missing_res.status_code == 404


def test_confirm_quote_not_found_returns_404():
    res = client.post("/transactions/confirm", json={"quote_id": "QTE-not-exists"})
    assert res.status_code == 404


def test_confirm_quote_expired_returns_422():
    _create_rate(
        rate_date="2026-03-02",
        base_currency="USD",
        quote_currency="PHP",
        side="SELL",
        rate="58.1000",
    )
    quote_res = client.post(
        "/quotes",
        json={
            "timestamp": "2026-03-02T10:00:00+08:00",
            "base_currency": "USD",
            "quote_currency": "PHP",
            "side": "SELL",
            "foreign_amount": "100.00",
        },
    )
    assert quote_res.status_code == 200
    quote_id = quote_res.json()["quote_id"]

    db = SessionLocal()
    try:
        quote = quote_repository.get_by_quote_id(db, quote_id=quote_id)
        quote.expires_at = datetime.utcnow() - timedelta(minutes=1)
        db.add(quote)
        db.commit()
    finally:
        db.close()

    confirm_res = client.post("/transactions/confirm", json={"quote_id": quote_id})
    assert confirm_res.status_code == 422


def test_calculators_buy_and_sell_direct_paths():
    buy = get_calculator("BUY")
    sell = get_calculator("SELL")

    buy_result = buy.calculate(
        rate=Decimal("57.2500"),
        foreign_amount=Decimal("100.00"),
        base_amount=None,
    )
    sell_result = sell.calculate(
        rate=Decimal("58.5000"),
        foreign_amount=Decimal("100.00"),
        base_amount=None,
    )

    assert buy_result.effective_rate == Decimal("57.2500")
    assert sell_result.effective_rate == Decimal("58.5000")
    assert buy_result.base_amount != sell_result.base_amount


def test_rate_repository_direct_get_update_delete():
    _create_rate(
        rate_date="2026-03-03",
        base_currency="EUR",
        quote_currency="PHP",
        side="BUY",
        rate="61.2500",
    )

    db = SessionLocal()
    try:
        rate = rate_repository.get_by_composite(
            db,
            rate_date=datetime.strptime("2026-03-03", "%Y-%m-%d").date(),
            base_currency="EUR",
            quote_currency="PHP",
            side="BUY",
        )
        assert rate is not None
        assert Decimal(rate.rate) == Decimal("61.2500")

        updated = rate_repository.update(
            db,
            rate_date=rate.rate_date,
            base_currency=rate.base_currency,
            quote_currency=rate.quote_currency,
            side=rate.side,
            rate=Decimal("61.9000"),
        )
        assert updated is not None
        assert Decimal(updated.rate) == Decimal("61.9000")

        deleted = rate_repository.delete(
            db,
            rate_date=rate.rate_date,
            base_currency=rate.base_currency,
            quote_currency=rate.quote_currency,
            side=rate.side,
        )
        assert deleted is True
    finally:
        db.close()


def test_quote_ttl_config_is_valid_integer():
    assert isinstance(QUOTE_TTL_MINUTES, int)
    assert QUOTE_TTL_MINUTES > 0
