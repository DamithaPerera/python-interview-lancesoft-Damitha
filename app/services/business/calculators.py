from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

ROUND_BASE_TO = Decimal("0.01")
ROUND_FOREIGN_TO = Decimal("0.01")


@dataclass(frozen=True)
class CalculationResult:
    foreign_amount: Decimal
    base_amount: Decimal
    effective_rate: Decimal
    fee_amount: Decimal
    rounding_adjustment: Decimal


class TransactionCalculator:
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


class BuyCalculator(TransactionCalculator):
    def calculate(
        self,
        *,
        rate: Decimal,
        foreign_amount: Decimal | None,
        base_amount: Decimal | None,
    ) -> CalculationResult:
        if foreign_amount is None:
            raw_foreign = base_amount * rate
            foreign_amount = self._round(raw_foreign, ROUND_FOREIGN_TO)
            rounding_adj = foreign_amount - raw_foreign
        else:
            raw_base = foreign_amount / rate
            base_amount = self._round(raw_base, ROUND_BASE_TO)
            rounding_adj = base_amount - raw_base

        return CalculationResult(
            foreign_amount=foreign_amount,
            base_amount=base_amount,
            effective_rate=rate,
            fee_amount=Decimal("0"),
            rounding_adjustment=rounding_adj,
        )


class SellCalculator(TransactionCalculator):
    def calculate(
        self,
        *,
        rate: Decimal,
        foreign_amount: Decimal | None,
        base_amount: Decimal | None,
    ) -> CalculationResult:
        if foreign_amount is None:
            raw_foreign = base_amount * rate
            foreign_amount = self._round(raw_foreign, ROUND_FOREIGN_TO)
            rounding_adj = foreign_amount - raw_foreign
        else:
            raw_base = foreign_amount / rate
            base_amount = self._round(raw_base, ROUND_BASE_TO)
            rounding_adj = base_amount - raw_base

        return CalculationResult(
            foreign_amount=foreign_amount,
            base_amount=base_amount,
            effective_rate=rate,
            fee_amount=Decimal("0"),
            rounding_adjustment=rounding_adj,
        )


def get_calculator(side: str) -> TransactionCalculator:
    normalized = side.upper()
    if normalized == "BUY":
        return BuyCalculator()
    if normalized == "SELL":
        return SellCalculator()
    raise ValueError("Unsupported side")
