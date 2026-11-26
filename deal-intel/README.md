# Black Friday Deal Intelligence 2026

Window: 26–30 November 2026 (Black Friday 27 Nov, Cyber Monday 30 Nov).

- `deals.json` — tracked deals with their state. Each hourly run reads it, rechecks, and updates it.
- `reports/` — one report per run that found something new or changed. Runs with no change write no report.

## Verification levels (used in every report)
- **V3 Verified** — price read on the retailer's own product page during the run.
- **V2 Corroborated** — same price reported by 2+ independent outlets the same day; not read on the retailer page.
- **V1 Single-source** — one outlet only. Not eligible for "Exceptional".
- **EST** — an estimate (shipping, duty, BDT conversion). Always labelled.

## Ratings
Exceptional / Strong / Good / Misleading. "Exceptional" needs V2+, a genuine discount against a
normal (not inflated) reference price, a reliable seller and long-term usefulness.

## Rules
No purchases, no sign-ups, no payment details, no accounts. Historical prices are never invented:
if no price history was found, the report says so.
