"""
Price Watcher - Product Price Monitor
=====================================
Monitors product pages and sends an email alert when a configured deal is detected.
"""

import sqlite3
import smtplib
import time
import logging
import json
import sys
import getpass
from pathlib import Path
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import requests
from bs4 import BeautifulSoup

from config import EMAIL_CONFIG, PRODUCTS, CHECK_INTERVAL_HOURS, DB_PATH

# ──────────────────────────────────────────
# Logging
# ──────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("watcher.log"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)

# ──────────────────────────────────────────
# Database
# ──────────────────────────────────────────
def init_db():
    """Creates tables if they don't exist."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS price_history (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            product    TEXT NOT NULL,
            price      REAL NOT NULL,
            url        TEXT NOT NULL,
            checked_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()
    log.info("Database ready.")


def save_price(product: str, price: float, url: str):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO price_history (product, price, url) VALUES (?, ?, ?)",
        (product, price, url)
    )
    conn.commit()
    conn.close()


def lowest_historical_price(product: str) -> float | None:
    """Returns the lowest price ever recorded for a product."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute(
        "SELECT MIN(price) FROM price_history WHERE product = ?", (product,)
    )
    result = cursor.fetchone()[0]
    conn.close()
    return result


def average_historical_price(product: str) -> float | None:
    """Returns the average of the last 30 records for discount calculation."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute(
        """SELECT AVG(price) FROM (
               SELECT price FROM price_history
               WHERE product = ?
               ORDER BY checked_at DESC
               LIMIT 30
           )""",
        (product,)
    )
    result = cursor.fetchone()[0]
    conn.close()
    return result


# ──────────────────────────────────────────
# Scraping
# ──────────────────────────────────────────
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    # Keep Brotli out of the request because the lightweight requests setup
    # does not install a Brotli decoder. This lets servers return gzip/deflate
    # responses that requests can decode reliably.
    "Accept-Encoding": "gzip, deflate",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


def _extract_jsonld_price(soup: BeautifulSoup) -> float | None:
    """Read a product price from Schema.org JSON-LD, when a page provides it."""
    scripts = soup.find_all("script", attrs={"type": "application/ld+json"})

    for script in scripts:
        raw = script.string or script.get_text()
        try:
            payload = json.loads(raw)
        except (TypeError, json.JSONDecodeError):
            continue

        nodes = payload if isinstance(payload, list) else [payload]
        for node in nodes:
            if not isinstance(node, dict):
                continue

            offers = node.get("offers", [])
            if isinstance(offers, dict):
                offers = [offers]
            if not isinstance(offers, list):
                offers = []

            for offer in offers:
                if not isinstance(offer, dict):
                    continue
                candidates = [offer]
                specifications = offer.get("priceSpecification", [])
                if isinstance(specifications, dict):
                    specifications = [specifications]
                if isinstance(specifications, list):
                    candidates.extend(specifications)

                for candidate in candidates:
                    for key in ("price", "lowPrice"):
                        if key in candidate:
                            price = _parse_price(str(candidate[key]))
                            if price is not None:
                                return price

    return None


def fetch_product_price(url: str) -> float | None:
    """
    Scrapes a product price from a retailer page.

    Structured Schema.org data is checked first, followed by legacy retailer
    HTML selectors for backwards compatibility with the original project.
    Returns the price as a float, or None if it can't be found.
    """
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        structured_price = _extract_jsonld_price(soup)
        if structured_price is not None:
            return structured_price

        # Selectors in order of priority
        selectors = [
            {"class": "a-price-whole"},
            {"id": "priceblock_ourprice"},
            {"id": "priceblock_dealprice"},
            {"class": "a-offscreen"},
        ]

        for sel in selectors:
            el = soup.find(attrs=sel)
            if el:
                raw = el.get_text().strip()
                price = _parse_price(raw)
                if price is not None:
                    return price

        log.warning("Price not found on page: %s", url)
        return None

    except requests.RequestException as e:
        log.error("Error accessing %s: %s", url, e)
        return None


def _parse_price(text: str) -> float | None:
    """Converts a price string (e.g. '$1,299.90') to a float."""
    import re
    digits = re.sub(r"[^\d.]", "", text)
    parts = digits.split(".")
    if len(parts) > 2:
        digits = "".join(parts[:-1]) + "." + parts[-1]
    try:
        return float(digits)
    except ValueError:
        return None


# ──────────────────────────────────────────
# Deal detection
# ──────────────────────────────────────────
def check_product(config: dict) -> dict | None:
    """
    Checks a product and returns a dict with deal info,
    or None if no deal was found.
    """
    name        = config["name"]
    url         = config["url"]
    target_price   = config.get("target_price")      # fixed price threshold
    min_discount   = config.get("min_discount", 0)   # % drop from historical average

    log.info("Checking: %s", name)
    current_price = fetch_product_price(url)

    if current_price is None:
        return None

    save_price(name, current_price, url)
    log.info("  Current price: $%.2f", current_price)

    alerts = []

    # ── Criterion 1: price below fixed target ─────
    if target_price and current_price <= target_price:
        alerts.append(
            f"Below target price! ${current_price:.2f} ≤ ${target_price:.2f}"
        )

    # ── Criterion 2: discount vs historical average ─────
    if min_discount > 0:
        avg = average_historical_price(name)
        if avg and avg > 0:
            actual_discount = ((avg - current_price) / avg) * 100
            log.info("  Historical avg: $%.2f | Discount: %.1f%%", avg, actual_discount)
            if actual_discount >= min_discount:
                alerts.append(
                    f"{actual_discount:.1f}% below historical average! "
                    f"(was ${avg:.2f}, now ${current_price:.2f})"
                )
        else:
            log.info("  Not enough history to calculate discount yet.")

    if alerts:
        return {
            "name": name,
            "url": url,
            "current_price": current_price,
            "alerts": alerts,
        }

    return None


# ──────────────────────────────────────────
# Email
# ──────────────────────────────────────────
def build_email_body(deals: list[dict]) -> str:
    """Builds the HTML body for the alert email."""
    rows = []
    for d in deals:
        rows.append(f"<h2>{d['name']}</h2>")
        rows.append(f"<p><strong>Current price:</strong> ${d['current_price']:.2f}</p>")
        for alert in d["alerts"]:
            rows.append(f"<p>{alert}</p>")
        rows.append(f'<p><a href="{d["url"]}">View product page</a></p>')
        rows.append("<hr>")

    return f"""
    <html><body>
    <h1>Price Watcher — Deal Alert!</h1>
    {"".join(rows)}
    <p style="color:gray;font-size:12px">
        Checked on {datetime.now().strftime("%Y-%m-%d at %H:%M")}
    </p>
    </body></html>
    """


def send_email(deals: list[dict]):
    cfg = EMAIL_CONFIG
    missing = [key for key in ("sender", "password", "recipient") if not cfg.get(key)]
    if missing:
        raise RuntimeError(
            "Missing email configuration. Set PRICE_WATCHER_EMAIL_SENDER, "
            "PRICE_WATCHER_EMAIL_PASSWORD and PRICE_WATCHER_EMAIL_RECIPIENT."
        )
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Price Watcher — {len(deals)} deal(s) found!"
    msg["From"]    = cfg["sender"]
    msg["To"]      = cfg["recipient"]

    html = build_email_body(deals)
    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP(cfg["smtp_host"], cfg["smtp_port"]) as server:
            server.ehlo()
            server.starttls()
            server.login(cfg["sender"], cfg["password"])
            server.sendmail(cfg["sender"], cfg["recipient"], msg.as_string())
        log.info("Email sent to %s", cfg["recipient"])
    except Exception as e:
        log.error("Failed to send email: %s", e)


def test_email_connection():
    """Send one clearly labelled test alert using credentials entered locally."""
    sender = EMAIL_CONFIG.get("sender") or input("Gmail remetente: ").strip()
    recipient = EMAIL_CONFIG.get("recipient") or input("E-mail destinatário: ").strip()
    password = EMAIL_CONFIG.get("password") or getpass.getpass(
        "App Password do Gmail (entrada oculta): "
    ).strip()

    EMAIL_CONFIG.update({
        "sender": sender,
        "recipient": recipient,
        "password": password,
    })
    send_email([
        {
            "name": "Price Watcher test",
            "url": "https://www.jbhifi.com.au/products/apple-airpods-4-with-active-noise-cancellation",
            "current_price": 249.99,
            "alerts": ["Test alert"],
        }
    ])


def setup_email_config():
    """Save local email settings to the ignored .env file."""
    sender = input("Gmail remetente: ").strip()
    recipient = input("E-mail destinatário: ").strip()
    password = getpass.getpass(
        "App Password do Gmail (entrada oculta): "
    ).strip()
    if not sender or not recipient or not password:
        raise RuntimeError("Remetente, destinatário e App Password são obrigatórios.")

    env_path = Path(__file__).with_name(".env")
    env_path.write_text(
        "\n".join(
            [
                f"PRICE_WATCHER_EMAIL_SENDER={sender}",
                f"PRICE_WATCHER_EMAIL_PASSWORD={password}",
                f"PRICE_WATCHER_EMAIL_RECIPIENT={recipient}",
                "PRICE_WATCHER_INTERVAL_HOURS=6",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(f"Configuração salva localmente em {env_path.name}. O arquivo está no .gitignore.")


# ──────────────────────────────────────────
# Main loop
# ──────────────────────────────────────────
def run_cycle():
    """Runs a full check across all products."""
    log.info("=" * 50)
    log.info("Starting check cycle...")
    deals = []

    for product in PRODUCTS:
        result = check_product(product)
        if result:
            deals.append(result)
        # Small pause between products to avoid rate limiting
        time.sleep(3)

    if deals:
        log.info("🎉 %d deal(s) found! Sending email...", len(deals))
        send_email(deals)
    else:
        log.info("No deals found this cycle.")

    log.info("Next check in %s hour(s).", CHECK_INTERVAL_HOURS)


def main():
    init_db()
    log.info("Price Watcher started!")

    if "--setup-email" in sys.argv:
        setup_email_config()
        return

    if "--test-email" in sys.argv:
        test_email_connection()
        return

    if "--once" in sys.argv:
        run_cycle()
        return

    while True:
        run_cycle()
        time.sleep(CHECK_INTERVAL_HOURS * 3600)


if __name__ == "__main__":
    main()
