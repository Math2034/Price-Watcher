"""Runtime configuration for Price Watcher.

Keep real credentials in environment variables or a local .env file that is
never committed to GitHub.
"""

import os
from pathlib import Path


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer") from exc


DB_PATH = os.getenv("PRICE_WATCHER_DB_PATH", "prices.db")
CHECK_INTERVAL_HOURS = _env_int("PRICE_WATCHER_INTERVAL_HOURS", 6)

EMAIL_CONFIG = {
    "smtp_host": os.getenv("PRICE_WATCHER_SMTP_HOST", "smtp.gmail.com"),
    "smtp_port": _env_int("PRICE_WATCHER_SMTP_PORT", 587),
    "sender": os.getenv("PRICE_WATCHER_EMAIL_SENDER", ""),
    "password": os.getenv("PRICE_WATCHER_EMAIL_PASSWORD", ""),
    "recipient": os.getenv("PRICE_WATCHER_EMAIL_RECIPIENT", ""),
}

# Add real products locally. Keep URLs and personal product lists out of commits
# when they contain private or account-specific information.
PRODUCTS: list[dict] = []

# Example product configuration:
#
# PRODUCTS = [
#     {
#         "name": "Example product",
#         "url": "https://www.amazon.com/dp/REPLACE_ME",
#         "target_price": 699.00,
#         "min_discount": 10,
#     },
# ]
