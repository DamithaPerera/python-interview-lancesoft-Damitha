from __future__ import annotations

import os

DATABASE_URL_DEFAULT = "sqlite:///./fx.db"
QUOTE_TTL_MINUTES = int(os.getenv("QUOTE_TTL_MINUTES", "15"))
