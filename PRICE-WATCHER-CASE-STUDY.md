# Price Watcher — Automation Case Study

## One-line summary

Personal Python automation that monitors product prices, stores price history and sends an email when a configured deal rule is met.

> This is a personal portfolio project. It is evidence of practical ability, not professional client experience.

## Problem

Manually checking prices is repetitive and easy to forget. A user needs a reliable way to monitor a product and be notified when the price reaches a chosen threshold or drops by a configured percentage.

## Objective

Build a small, maintainable workflow that:

1. checks configured product pages;
2. extracts the displayed price;
3. records the result for future comparison;
4. applies configurable alert rules; and
5. sends a clear email notification when a rule is met.

## Solution

Price Watcher uses scheduled polling to request product pages, parse prices from structured data or page content, persist observations in SQLite, compare them with alert rules, and send an HTML email when a deal is detected.

## Technologies and integrations

- Python
- Requests and BeautifulSoup
- Schema.org JSON-LD parsing with a fallback parser
- SQLite
- SMTP email
- Logging and environment-based configuration
- unittest

## Evidence of implementation

- The automated test suite covers currency parsing, invalid values and JSON-LD product prices.
- The current test run completed with 4 tests passing.
- The project includes defensive configuration checks, logging and a troubleshooting record for a real retailer response.
- Email credentials are loaded from local environment configuration and excluded from version control.

## Business value demonstrated

The same pattern can be adapted to repetitive checks such as competitor-price monitoring, stock alerts, scheduled reports, lead follow-up reminders or internal operations notifications. The value is not the retail price itself; it is reducing manual checking and making an important event visible at the right time.

## Current limitations

- Retailer page layouts can change.
- Some sites rate-limit or block automated requests.
- The project currently uses polling rather than a hosted scheduler.
- It is not a multi-user production application.

## Next improvements

- Add saved HTML fixtures for parser regression tests.
- Add retailer-specific parsers, retries and backoff.
- Add a small dashboard for price history.
- Run checks through a hosted scheduler or GitHub Actions workflow.

## Honest interview explanation

“I have not yet delivered automation as a paid client project. I built Price Watcher as a personal portfolio project to practise the full workflow: HTTP requests, HTML and JSON-LD parsing, SQLite persistence, configurable rules, email delivery, testing and troubleshooting. I can explain the design decisions and the limitations, and I am looking for an entry-level opportunity where I can apply that foundation under supervision.”

