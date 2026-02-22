# ================================================================
#  config.py — Set everything up here before running the bot
# ================================================================

# ── Where to save the database ──────────────────────────────────
DB_PATH = "prices.db"

# ── How often the bot checks prices (in hours) ──────────────────
CHECK_INTERVAL_HOURS = 6

# ── Email settings ───────────────────────────────────────────────
# Tip: use a Gmail account with an "App Password" (not your regular password)
# How to generate one: https://myaccount.google.com/apppasswords
EMAIL_CONFIG = {
    "smtp_host":  "smtp.gmail.com",
    "smtp_port":  587,
    "sender":     "your_email@gmail.com",   # ← replace
    "password":   "xxxx xxxx xxxx xxxx",    # ← Gmail app password
    "recipient":  "your_email@gmail.com",   # ← can be the same address
}

# ── Products to monitor ──────────────────────────────────────────
# For each product:
#   name          → label shown in the email alert
#   url           → Amazon product link
#   target_price  → alert if price drops BELOW this value (optional)
#   min_discount  → alert if price drops X% below historical average (optional)
#
# You can use one criterion, both, or neither per product.

PRODUCTS = [
    {
        "name": "Dell Inspiron 15 Laptop",
        "url": "https://www.amazon.com/dp/XXXXXXXXXX",  # ← replace with real link
        "target_price": 699.00,    # alert if price drops below $699
        "min_discount": 10,        # alert if price drops 10%+ vs historical average
    },
    {
        "name": "Kingston 1TB SSD",
        "url": "https://www.amazon.com/dp/XXXXXXXXXX",  # ← replace with real link
        "target_price": 79.00,
        "min_discount": 15,
    },
    # Add as many products as you want following the same pattern...
]