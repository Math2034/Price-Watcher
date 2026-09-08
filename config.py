"""Runtime configuration for Price Watcher.

Keep real credentials in environment variables or a local .env file that is
never committed to GitHub.
"""

import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - dependency is installed from requirements.txt
    load_dotenv = None


if load_dotenv is not None:
    load_dotenv(dotenv_path=Path(__file__).with_name(".env"))


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

# Add real products in the ignored config_local.py file. Keeping personal
# product lists outside the tracked config prevents accidental publication.
try:
    from config_local import PRODUCTS as LOCAL_PRODUCTS
except ModuleNotFoundError:
    LOCAL_PRODUCTS = []

PRODUCTS: list[dict] = LOCAL_PRODUCTS

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
