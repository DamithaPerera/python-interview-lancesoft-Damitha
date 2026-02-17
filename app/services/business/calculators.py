from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

from app.core.config import BUY_SPREAD_BPS, FEE_PERCENT, SELL_SPREAD_BPS

ROUND_BASE_TO = Decimal("0.01")
ROUND_FOREIGN_TO = Decimal("0.01")
ROUND_RATE_TO = Decimal("0.00000001")


@dataclass(frozen=True)
class CalculationResult:
    foreign_amount: Decimal
    base_amount: Decimal
    effective_rate: Decimal
    fee_amount: Decimal
    rounding_adjustment: Decimal


class TransactionCalculator:
    spread_bps = Decimal("0")

    def calculate(
        self,
        *,
        rate: Decimal,
        foreign_amount: Decimal | None,
        base_amount: Decimal | None,
    ) -> CalculationResult:
        raise NotImplementedError

    def _round(self, amount: Decimal, quantum: Decimal) -> Decimal:
        return amount.quantize(quantum, rounding=ROUND_HALF_UP)

    def _effective_rate(self, rate: Decimal) -> Decimal:
        multiplier = Decimal("1") + (self.spread_bps / Decimal("10000"))
        return self._round(rate * multiplier, ROUND_RATE_TO)

    def _fee_for_base(self, base_amount: Decimal) -> Decimal:
        if FEE_PERCENT <= 0:
            return Decimal("0")
        fee_raw = (base_amount * FEE_PERCENT) / Decimal("100")
        return self._round(fee_raw, ROUND_BASE_TO)


class BuyCalculator(TransactionCalculator):
    spread_bps = BUY_SPREAD_BPS

    def calculate(
        self,
        *,
        rate: Decimal,
        foreign_amount: Decimal | None,
        base_amount: Decimal | None,
    ) -> CalculationResult:
        effective_rate = self._effective_rate(rate)
        if foreign_amount is None:
            raw_foreign = base_amount * effective_rate
            foreign_amount = self._round(raw_foreign, ROUND_FOREIGN_TO)
            rounding_adj = foreign_amount - raw_foreign
        else:
            raw_base = foreign_amount / effective_rate
            base_amount = self._round(raw_base, ROUND_BASE_TO)
            rounding_adj = base_amount - raw_base

        fee_amount = self._fee_for_base(base_amount)
        return CalculationResult(
            foreign_amount=foreign_amount,
            base_amount=base_amount,
            effective_rate=effective_rate,
            fee_amount=fee_amount,
            rounding_adjustment=rounding_adj,
        )


class SellCalculator(TransactionCalculator):
    spread_bps = SELL_SPREAD_BPS

    def calculate(
        self,
        *,
        rate: Decimal,
        foreign_amount: Decimal | None,
        base_amount: Decimal | None,
    ) -> CalculationResult:
        effective_rate = self._effective_rate(rate)
        if foreign_amount is None:
            raw_foreign = base_amount * effective_rate
            foreign_amount = self._round(raw_foreign, ROUND_FOREIGN_TO)
            rounding_adj = foreign_amount - raw_foreign
        else:
            raw_base = foreign_amount / effective_rate
            base_amount = self._round(raw_base, ROUND_BASE_TO)
            rounding_adj = base_amount - raw_base

        fee_amount = self._fee_for_base(base_amount)
        return CalculationResult(
            foreign_amount=foreign_amount,
            base_amount=base_amount,
            effective_rate=effective_rate,
            fee_amount=fee_amount,
            rounding_adjustment=rounding_adj,
        )


def get_calculator(side: str) -> TransactionCalculator:
    normalized = side.upper()
    if normalized == "BUY":
        return BuyCalculator()
    if normalized == "SELL":
        return SellCalculator()
    raise ValueError("Unsupported side")
