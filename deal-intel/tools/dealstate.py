#!/usr/bin/env python3
"""State helper for the hourly deal-intelligence task. Standard library only.

Run from the repository root:  python3 -I deal-intel/tools/dealstate.py <command> [...]
  plan                       decide this run's cycle; list V3 deals to monitor and leads due for recovery
  observe ID AMOUNT CUR TYPE URL [--label L] [--stock yes|no|unknown] [--note N]
                             append a price observation (TYPE: seller_page, category_page,
                             reference_rrp, previous_price, article, history_source)
  attempt ID RESULT REASON   record a lead-recovery attempt and schedule the next one
                             (RESULT: verified, blocked, temporary, not_found, no_new_info)
  alert-check ID LEVEL AMOUNT    print SEND or SKIP for a push alert (LEVEL: exceptional, lead, buy_now)
  alert-record ID LEVEL AMOUNT   log an alert that was sent
  deep-done                  record that the discovery/recovery cycle ran
  validate                   check state consistency (exit code 1 on problems)
"""
import json, sys, datetime as dt
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEALS, HIST = ROOT / "deals.json", ROOT / "price-history.json"
DEEP_EVERY = dt.timedelta(hours=2, minutes=45)   # 3-hour cycle, tolerant of run drift
STALE_AFTER = dt.timedelta(hours=3)
LEADS_PER_CYCLE = 8
REALERT_DROP = 0.05                              # re-alert only on a further >=5% price drop
LEVEL_RANK = {"lead": 1, "exceptional": 2, "buy_now": 3}
OBS_TYPES = {"seller_page", "category_page", "reference_rrp", "previous_price", "article", "history_source"}
BACKOFF = {  # hours until next attempt, by result; blocked escalates with repeated failures
    "temporary": [1, 3, 3], "blocked": [6, 6, 12], "no_new_info": [3, 6, 12]}
PRIORITY_BASE = {"exceptional": 40, "strong": 30, "good": 20, "watch": 15}

now = lambda: dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
iso = lambda t: t.strftime("%Y-%m-%dT%H:%M:%SZ")

def parse(s):
    if not s: return None
    s = s.strip().replace("Z", "+00:00")
    if len(s) == 16: s += ":00"                    # tolerate 2026-11-27T14:50
    if "+" not in s[10:]: s += "+00:00"
    try: return dt.datetime.fromisoformat(s)
    except ValueError: return None

def load(p, default):
    return json.loads(p.read_text()) if p.exists() else default

def save(p, obj):
    p.write_text(json.dumps(obj, indent=1, ensure_ascii=False) + "\n")

def find(d, did):
    for e in d["deals"]:
        if e["id"] == did: return e
    sys.exit(f"unknown deal id: {did}")

def is_v3(e): return str(e.get("verification", "")).startswith("V3")
def is_lead(e): return str(e.get("rating", "")).startswith("UNVERIFIED") or e.get("status") in ("needs-recheck", "watch")

def priority(e, t):
    r = str(e.get("provisional_rating") or e.get("rating") or "").lower()
    score = next((v for k, v in PRIORITY_BASE.items() if k in r), 10)
    score += {"C": 6, "D": 6, "A": 5, "B": 5}.get(e.get("section"), 0)
    dl = parse(e.get("deadline_utc"))
    if dl and dl > t: score += 15 if dl - t < dt.timedelta(hours=24) else 5
    rec = e.get("recovery", {})
    if rec.get("last_result") == "temporary": score += 10
    if rec.get("parked"): score -= 25
    return score

def cmd_plan(d):
    t = now(); wf = d.setdefault("workflow", {})
    last = parse(wf.get("last_deep_cycle_at"))
    deep = last is None or t - last >= DEEP_EVERY
    out = {"now": iso(t), "cycle": "deep" if deep else "monitor",
           "last_deep_cycle_at": wf.get("last_deep_cycle_at"),
           "monitor_v3": [], "stale_v3": [], "leads_due": [], "leads_deferred": 0,
           "discovery_focus": None}
    for e in d["deals"]:
        if is_v3(e) and e.get("status") in ("active", "needs-recheck"):
            out["monitor_v3"].append(e["id"])
            lv = parse(e.get("last_verified_at"))
            if not lv or t - lv > STALE_AFTER: out["stale_v3"].append(e["id"])
    if deep:
        due = []
        for e in d["deals"]:
            if is_v3(e) or not is_lead(e) or e.get("status") in ("expired", "info"): continue
            nxt = parse(e.get("recovery", {}).get("next_check_after"))
            if nxt and nxt > t: out["leads_deferred"] += 1; continue
            due.append((priority(e, t), e["id"]))
        due.sort(reverse=True)
        out["leads_due"] = [i for _, i in due[:LEADS_PER_CYCLE]]
        out["leads_deferred"] += max(0, len(due) - LEADS_PER_CYCLE)
        rot = wf.get("discovery_rotation", ["A", "B", "C", "D"])
        k = wf.get("deep_cycles_done", 0) % len(rot)
        out["discovery_focus"] = {"all_sections": ["A", "B", "C", "D"], "extra_depth": rot[k]}
    print(json.dumps(out, indent=1))

def cmd_observe(d, a):
    did, amount, cur, typ, url = a[:5]
    if typ not in OBS_TYPES: sys.exit(f"TYPE must be one of {sorted(OBS_TYPES)}")
    opts = dict(zip(a[5::2], a[6::2]))
    find(d, did)
    h = load(HIST, {"observations": {}})
    obs = {"at": iso(now()), "amount": float(amount), "currency": cur.upper(), "type": typ, "url": url,
           "label": opts.get("--label"), "stock": opts.get("--stock", "unknown"), "note": opts.get("--note")}
    h["observations"].setdefault(did, []).append(obs)
    save(HIST, h); refresh_intel(d, h, did); save(DEALS, d)
    print("recorded", json.dumps(obs, ensure_ascii=False))

def refresh_intel(d, h, did):
    rows = h["observations"].get(did, [])
    e = find(d, did); pi = e.setdefault("price_intel", {})
    pick = lambda typs: [r for r in rows if r["type"] in typs]
    rrp = pick({"reference_rrp"}); prev = pick({"previous_price"}); seller = pick({"seller_page", "category_page"})
    if rrp: pi["rrp"] = {k: rrp[-1][k] for k in ("amount", "currency", "url", "at")}
    if prev: pi["previous_retailer_price"] = {k: prev[-1][k] for k in ("amount", "currency", "url", "at")}
    if seller:
        cur = seller[-1]; low = min(seller, key=lambda r: r["amount"])
        pi["current_price"] = {k: cur[k] for k in ("amount", "currency", "url", "at", "type")}
        pi["lowest_observed_by_us"] = {"amount": low["amount"], "currency": low["currency"], "at": low["at"],
                                       "since": seller[0]["at"], "observations": len(seller)}
    hs = pick({"history_source"})
    # A historical-low claim is only allowed with an external price-history source on record.
    pi["historical_low_claim"] = ({"supported": True, "source": hs[-1]["url"], "note": hs[-1].get("note")}
                                  if hs else {"supported": False, "note": "no price-history source recorded; do not claim a historical low"})

def cmd_attempt(d, a):
    did, result, reason = a[0], a[1], " ".join(a[2:])
    e = find(d, did); t = now(); rec = e.setdefault("recovery", {})
    rec.setdefault("attempts", []).append({"at": iso(t), "result": result, "reason": reason})
    rec["attempts"] = rec["attempts"][-10:]
    rec["last_result"], rec["last_reason"] = result, reason
    if result == "verified":
        rec.pop("next_check_after", None); rec["parked"] = False
    elif result == "not_found":
        e["status"] = "expired"; rec.pop("next_check_after", None)
    else:
        n = sum(1 for x in rec["attempts"] if x["result"] == result)  # seeded "access_test" rows never count
        hours = BACKOFF.get(result, [6])[min(n, 3) - 1]
        rec["next_check_after"] = iso(t + dt.timedelta(hours=hours))
        rec["parked"] = result == "blocked" and n >= 3
        if rec["parked"]:
            rec["why_unverified"] = ("Seller page repeatedly unreadable (" + reason + "); no alternative primary source "
                                     "confirmed it. Rechecked every 12h or when discovery finds new evidence.")
    save(DEALS, d); print(json.dumps({did: rec}, indent=1))

def cmd_alert_check(d, a, record=False):
    did, level, amount = a[0], a[1], float(a[2])
    if level not in LEVEL_RANK: sys.exit("LEVEL must be exceptional, lead or buy_now")
    log = d.setdefault("alerts_log", [])
    prior = [x for x in log if x["deal_id"] == did]
    if record:
        log.append({"deal_id": did, "level": level, "amount": amount, "at": iso(now())})
        save(DEALS, d); print("logged"); return
    if not prior: print("SEND: first alert for this deal"); return
    best = max(prior, key=lambda x: (LEVEL_RANK[x["level"]], x["at"]))
    if LEVEL_RANK[level] > LEVEL_RANK[best["level"]]:
        print(f"SEND: level upgrade {best['level']} -> {level}"); return
    amts = [x["amount"] for x in prior if LEVEL_RANK[x["level"]] >= LEVEL_RANK[level] and x["amount"] > 0]
    last_amt = min(amts) if amts else None
    if amount > 0 and last_amt and amount <= last_amt * (1 - REALERT_DROP):
        print(f"SEND: price fell >=5% since last alert ({last_amt} -> {amount})"); return
    print(f"SKIP: already alerted at {best['level']} ({best['at']}); no material change")

def cmd_deep_done(d):
    wf = d.setdefault("workflow", {})
    wf["last_deep_cycle_at"] = iso(now()); wf["deep_cycles_done"] = wf.get("deep_cycles_done", 0) + 1
    save(DEALS, d); print("deep cycle recorded", wf["last_deep_cycle_at"])

def cmd_validate(d):
    probs, t = [], now()
    for e in d["deals"]:
        r = str(e.get("rating", ""))
        if r.startswith(("Strong", "Exceptional")) and not is_v3(e):
            probs.append(f"{e['id']}: {r} without V3")
        if is_v3(e) and not e.get("primary_source_link"):
            probs.append(f"{e['id']}: V3 without primary_source_link")
        if e.get("alert_level") == "buy_now":
            c = e.get("checks", {})
            if not all(c.get(k, {}).get("verified") for k in ("price", "exact_config", "stock_purchasable", "london_fulfilment")):
                probs.append(f"{e['id']}: buy_now without all four C/D checks")
        claim = e.get("price_intel", {}).get("historical_low_claim", {})
        if "lowest ever" in json.dumps(e).lower() or "all-time low" in json.dumps(e).lower():
            if not claim.get("supported"): probs.append(f"{e['id']}: historical-low wording without a history_source")
    print("\n".join(probs) if probs else "OK"); sys.exit(1 if probs else 0)

if __name__ == "__main__":
    if len(sys.argv) < 2: sys.exit(__doc__)
    d = load(DEALS, None); c, a = sys.argv[1], sys.argv[2:]
    {"plan": lambda: cmd_plan(d), "observe": lambda: cmd_observe(d, a), "attempt": lambda: cmd_attempt(d, a),
     "alert-check": lambda: cmd_alert_check(d, a), "alert-record": lambda: cmd_alert_check(d, a, True),
     "deep-done": lambda: cmd_deep_done(d), "validate": lambda: cmd_validate(d)}.get(c, lambda: sys.exit(__doc__))()
