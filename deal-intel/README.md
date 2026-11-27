# Black Friday AI & Technology Deal Intelligence 2026

Window: 26–30 Nov 2026 (Black Friday 27 Nov, Cyber Monday 30 Nov). Scope updated 26 Nov. The previous broad-scope
state is kept in `archive/` for reference only.

## Scope (strict: nothing outside these four sections)
- **A. AI subscriptions and services.** Assistants, research and productivity tools, coding assistants, agents and
  automation, image/video/audio/design generation, APIs and inference, LLM platforms, AI BI/analytics. Global search;
  rank what is practical to pay for and use from Bangladesh first.
- **B. Servers, hosting and cloud.** VPS, dedicated, cloud, GPU rental, AI inference hosting, web/managed hosting,
  domains, storage and backup, databases, serverless, deployment platforms, CDN and networking. Global search;
  Bangladesh payment and usage practicality matters. Weigh renewal price, term length, CPU/RAM/storage/bandwidth value,
  GPU availability, hidden limits and cancellation terms.
- **C. iPhone only, London only.** Apple Store UK, authorised resellers, reputable UK retailers, trustworthy marketplace
  sellers, with verifiable delivery or collection in London. New, refurbished and open-box are kept clearly separate.
  No Android, and no prices from other countries.
- **D. Laptops (all brands), London only.** Same retailer and London rules as C. Exact configurations compared;
  AI-capable, high-RAM, dedicated-GPU, MacBook and developer machines prioritised.

**Excluded:** appliances, TVs, general electronics, Android, fashion, fitness, furniture, kitchen, household,
gaming consoles, and anything else outside A–D.

## Verification levels
- **V3** price read on the provider's or retailer's own page.
- **V2** 2+ independent sources agree.
- **V1** single source.
- **EST** estimate.

## Ratings and verification policy (updated 26 Nov)
Exceptional / Strong / Good / Not worthwhile / **UNVERIFIED**.
- Third-party deal articles are used **only to discover** deals.
- **Strong or Exceptional requires V3**: the price and terms were read on the retailer's or provider's own product or
  offer page, with the link and time recorded.
- If the seller's price cannot be confirmed, the deal is **UNVERIFIED** and is not ranked as a confirmed deal. It is
  listed separately with its provisional rating.
- An advertised percentage alone never justifies Exceptional. The deal must also be the right product or tier, have
  real utility, and have an acceptable renewal or long-term cost.

## Required fields per deal
`primary_source_link`, `last_verified_at` (UTC), `exact_config` (model, configuration or tier), `payable_price`,
`renewal_or_long_term_cost`, `eligibility` (geography and payment), `limitations`.

## Priorities by section
- **A. AI services:** real utility, usage limits and rate caps, API access, commercial-use rights.
- **B. Hosting:** infrastructure for AI agents, automation, databases and business apps (RAM, vCPU, NVMe, bandwidth,
  snapshots and backups, managed DBs, GPU availability, uptime and support).
- **D. Laptops:** AI development and local model experimentation (unified memory or VRAM first: 32GB+ RAM or 12GB+
  VRAM preferred), programming, long-term productivity, battery and build quality.

## Authorisation
Research, compare, monitor, rank and recommend only. No purchases, subscriptions, trials, accounts, payment details,
contracts or non-refundable payments.

## iPhone and laptop purchase-readiness checks (C and D; added 26 Nov)
Each C/D deal records four separate checks, each with evidence and a UTC time:
1. **Price verified:** price read on the seller's own page. A category or listing page counts as price discovery.
2. **Exact product/configuration verified:** model, storage, colour, and CPU/GPU/RAM/SSD for laptops, read on the
   product page.
3. **Stock and purchase availability verified:** the product page shows in stock, add-to-basket or buy, not "sold out"
   or "notify me".
4. **London fulfilment verified:** delivery to a London postcode or click-and-collect at a London store is shown as
   available.

**Alert levels**
- **BUY NOW:** rating is Exceptional and all four checks pass.
- **LEAD:** rating is Exceptional but checks 3 or 4 are open. It is labelled "availability unconfirmed", is never
  presented as confirmed, and is sent at most once per deal.
- Nothing is sent for anything below Exceptional.

A category page showing a price is never enough for BUY NOW.

## Run workflow (added 27 Nov)
Each hourly run starts with `python3 -I deal-intel/tools/dealstate.py plan`, which decides the cycle.

**Every run (monitor cycle): V3 deal monitoring**
- Re-read each active V3 deal on its `primary_source_link`.
- Record price, stock, expiry and terms, and log the price with `observe`.
- Update `last_verified_at` **only after a successful read**. A failed read is noted in `limitations` and never carries
  the old values forward.
- A V3 deal not re-read successfully for over 3 hours is shown as **stale** ("last confirmed HH:MM"). Stale evidence
  can't trigger an alert.

**Deep cycle: at least 2h45m since the last one, so about every 3 hours**
1. **Lead recovery:** `plan` lists up to 8 leads that are due, highest priority first. Priority comes from provisional
   rating, deadline within 24h and recent temporary errors.
   - For each lead, try the seller page (direct read, then WebFetch). Then try legitimate alternatives: the
     manufacturer's or official store page, another authorised UK retailer's product page, or the provider's official
     pricing, help, blog or newsroom page.
   - Record the outcome with `attempt`:
     - `temporary` (timeout, 5xx, truncated page): retry in 1h, then 3h.
     - `blocked` (bot protection): retry in 6h, 6h, then **parked** with a written `why_unverified`, checked only every
       12h or when new evidence appears.
     - `no_new_info`: retry in 3h, 6h, then 12h.
     - `not_found`: the deal is expired.
     - `verified`: the deal becomes V3.
   - Leads not due are skipped, so unchanged leads aren't re-checked without a reason.
   - Pages that can't be read are never worked around.
2. **Discovery:** search all four sections (A–D) for new promotions, plus extra depth in that cycle's rotating focus
   section. Only offers that look genuinely valuable become new leads. Each must be confirmed on the seller's page
   before it can be ranked.
3. Run `deep-done`.

## Price history (`price-history.json`)
- Append-only observations: `{at, amount, currency, type, url, label, stock, note}`.
- Types: `seller_page`, `category_page`, `reference_rrp`, `previous_price`, `article`, `history_source`.
- `observe` keeps each deal's `price_intel` up to date, keeping these separate: `rrp`, `previous_retailer_price`,
  `current_price` and `lowest_observed_by_us` (our own observations, with the date range).
- A **historical-low claim is allowed only when a `history_source` observation exists**, for example a price-history
  site entry with its URL. `validate` flags "lowest ever" or "all-time low" wording that has no such source.

## Alert de-duplication (`alerts_log`)
- Before any push, run `alert-check ID LEVEL AMOUNT`. Send only on `SEND`, then run `alert-record`.
- `SEND` happens only for:
  - the first alert for that deal,
  - a level upgrade (lead → exceptional → buy_now),
  - a further price drop of at least 5% below the lowest price already alerted.
- Everything else is `SKIP`.
- Downgrades, expiries and stock-outs go in the report, not in a push.
- Run `validate` before every commit. It checks that Strong or Exceptional has V3, BUY NOW has all four C/D checks, and
  historical-low claims are backed by a source.
