# Price Watcher

A Python bot that monitors Amazon product prices and sends you an email alert whenever it detects a deal.

## Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure the bot
#    Open config.py and fill in:
#      - Your email credentials
#      - The products you want to monitor (URL + alert criteria)

# 3. Run
python bot.py
```

## Gmail setup

Gmail won't accept your regular password for scripts. You need an **App Password**:

1. Go to: https://myaccount.google.com/apppasswords
2. Select "Other" and name it "Price Watcher"
3. Copy the generated 16-character password and paste it into `config.py`

## Adding products

Each product in `config.py` has 4 fields:

| Field | What it does |
|---|---|
| `name` | Label shown in the email alert |
| `url` | Amazon product link |
| `target_price` | Alert if price drops **below** this value |
| `min_discount` | Alert if price drops **X%** below historical average |

Both criteria work independently — use one, both, or neither per product.

## How it works

```
bot.py
  ├── Every X hours (configurable), checks all products
  ├── Scrapes the current price from Amazon
  ├── Saves the price to a local SQLite database (prices.db)
  ├── Compares against the fixed target and/or historical average
  └── If a deal is detected → sends an email alert
```

## Running in the background (Linux/Mac)

```bash
# Keeps running even after closing the terminal
nohup python bot.py &

# Watch the logs live
tail -f watcher.log
```

## Notes

- Amazon occasionally blocks scrapers. If it stops working, try increasing `CHECK_INTERVAL_HOURS` in `config.py` — the more spread out the requests, the less likely to get blocked.
- The historical average discount only kicks in after several data collection cycles. For the first day or two, only `target_price` alerts will fire.
