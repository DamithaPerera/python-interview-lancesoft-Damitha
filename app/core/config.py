from __future__ import annotations

import os
from decimal import Decimal

DATABASE_URL_DEFAULT = "sqlite:///./fx.db"
QUOTE_TTL_MINUTES = int(os.getenv("QUOTE_TTL_MINUTES", "15"))
BUY_SPREAD_BPS = Decimal(os.getenv("BUY_SPREAD_BPS", "0"))
SELL_SPREAD_BPS = Decimal(os.getenv("SELL_SPREAD_BPS", "0"))
FEE_PERCENT = Decimal(os.getenv("FEE_PERCENT", "0"))
