# Price Watcher

A Python automation project that monitors product prices and sends an email alert when a configured deal is detected.

This is a personal portfolio project demonstrating web requests, HTML parsing, SQLite persistence, scheduled checks and email automation.

## What problem it solves

Manually checking prices is repetitive and easy to forget. Price Watcher records price history and alerts the user when a product reaches a target price or drops by a chosen percentage compared with recent history.

## Technologies

- Python
- Requests and BeautifulSoup
- SQLite
- SMTP email
- Logging
- Scheduled polling

## How it works

1. Read the local product configuration.
2. Request each product page.
3. Parse the displayed price.
4. Save the result to SQLite.
5. Compare the current price with the configured rules.
6. Send an HTML email when a deal is detected.

## Setup

Create and activate a virtual environment, then install dependencies:

    python -m venv .venv
    source .venv/bin/activate        # macOS/Linux
    .venv\Scripts\Activate.ps1     # Windows PowerShell
    pip install -r requirements.txt

Add config.py locally. The repository keeps the committed product list empty so personal URLs and thresholds are not published accidentally.

## Environment variables

Email settings are read at runtime. Do not put passwords in config.py or commit them to GitHub.

### Windows PowerShell

    $env:PRICE_WATCHER_EMAIL_SENDER = "you@example.com"
    $env:PRICE_WATCHER_EMAIL_PASSWORD = "your-app-password"
    $env:PRICE_WATCHER_EMAIL_RECIPIENT = "you@example.com"
    $env:PRICE_WATCHER_INTERVAL_HOURS = "6"
    python bot.py

### macOS/Linux

    export PRICE_WATCHER_EMAIL_SENDER="you@example.com"
    export PRICE_WATCHER_EMAIL_PASSWORD="your-app-password"
    export PRICE_WATCHER_EMAIL_RECIPIENT="you@example.com"
    export PRICE_WATCHER_INTERVAL_HOURS="6"
    python bot.py

For Gmail, use an App Password rather than your normal account password. Keep the value private.

Optional variables:
- PRICE_WATCHER_SMTP_HOST (default: smtp.gmail.com)
- PRICE_WATCHER_SMTP_PORT (default: 587)
- PRICE_WATCHER_DB_PATH (default: prices.db)

## Running

    python bot.py

The bot checks products every six hours by default. Runtime database and log files are ignored by Git.

## Portfolio evidence

This project demonstrates:
- designing a small automation workflow;
- integrating HTTP requests and HTML parsing;
- persisting structured history in SQLite;
- implementing configurable business rules;
- generating and sending an HTML email;
- adding logging and defensive configuration handling.

## Current limitations

- Product page layouts can change and break selectors.
- Some retailers rate-limit or block automated requests.
- The project currently uses polling rather than a hosted scheduler.
- No web dashboard or multi-user authentication is included.

## Future improvements

- Add parser tests with saved HTML fixtures.
- Support retailer-specific parsers.
- Add retries and backoff for temporary request failures.
- Add a small dashboard for price history.
- Run checks through a scheduled GitHub Actions workflow or hosted worker.

## Disclaimer

Use the project responsibly and follow each retailer's terms of service and applicable rate limits.