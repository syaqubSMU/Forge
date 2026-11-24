"""Stored copy of the Grants.gov corpus (PRD hard rule 1 reversed, customer-approved for the demo).

What is stored: the sponsor's own list and detail records, the cleaned text the model will quote, a text hash,
and when each was retrieved. What is NOT stored: researcher profiles or any judgment. Every result is stamped
with the time the data was retrieved, and the run pipeline is unchanged: it simply receives stored records through
the same lister/detailer interface it used for live pulls.

  ingest(db)           refresh the store from Grants.gov (nightly, or the admin button) and log every API call
  sources(db)          (lister, detailer) that read the store, falling back to live pulls while the store is empty
"""
import hashlib
import json
import uuid
from datetime import date, datetime, timezone

from .db import now
from .sources import grants_gov as gg

DATE_FIELDS = ("close_date", "posting_date", "archive_date", "last_updated")


def _iso(d):
    return d.isoformat() if isinstance(d, date) else None


def _date(s):
    try:
        return date.fromisoformat(s) if s else None
    except ValueError:
        return None


def _flags(d: dict) -> list:
    """Recomputed on every read, so an archived record is flagged as of today, not as of the last ingest."""
    out = []
    if d.get("archive_date") and d["archive_date"] <= date.today():
        out.append("Archived on the sponsor site")
    if d.get("related_opportunity_ids"):
        out.append("Sponsor lists a related or replacement posting")
    return out


# ------------------------------------------------------------------ ingest
def ingest(db, statuses=("posted", "forecasted"), detail_window_months=12, lister=None, detailer=None,
           timeout=30.0, concurrency=8) -> dict:
    """List everything, then read full text for records that have none yet or close inside the window.
    Every Grants.gov request is written to api_calls."""
    lister = lister or gg.list_opportunities
    detailer = detailer or gg.fetch_details
    iid, t0 = uuid.uuid4().hex[:10], datetime.now(timezone.utc)

    def hook(endpoint, params, ok, status, latency_ms, error):
        db.q("INSERT INTO api_calls(at,source,endpoint,params,ok,http_status,latency_ms,error,ingest_id) VALUES(?,?,?,?,?,?,?,?,?)",
             (now(), "Grants.gov", endpoint, json.dumps(params), int(ok), status, latency_ms, error, iid), write=True)

    gg.call_hook = hook
    try:
        gg.clear_cache()
        listed = lister(statuses, timeout=timeout, cache_ttl_minutes=0)
        stamp = now()
        for r in listed:
            db.q("INSERT INTO opportunities(source_record_id,source_system,number,title,sponsor,agency_code,status,open_date,close_date,url,listed_at)"
                 " VALUES(?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(source_record_id) DO UPDATE SET number=excluded.number, title=excluded.title,"
                 " sponsor=excluded.sponsor, agency_code=excluded.agency_code, status=excluded.status, open_date=excluded.open_date,"
                 " close_date=excluded.close_date, url=excluded.url, listed_at=excluded.listed_at",
                 (r["source_record_id"], r.get("source_system", "Grants.gov"), r.get("number"), r.get("title"), r.get("sponsor"),
                  r.get("agency_code"), r.get("status"), _iso(r.get("open_date")), _iso(r.get("close_date")), r.get("url"), stamp), write=True)
        # records that have disappeared from the sponsor's list are not deleted; their status simply stops being refreshed
        have = {x["source_record_id"] for x in db.q("SELECT source_record_id FROM opportunities WHERE detail IS NOT NULL")}
        horizon = int(round(detail_window_months * 30.44))
        want = [r["source_record_id"] for r in listed
                if r["source_record_id"] not in have
                or (gg.days_until(r.get("close_date")) is not None and 0 <= gg.days_until(r.get("close_date")) <= horizon)]
        details, failures = detailer(want, timeout=timeout, concurrency=concurrency)
        dstamp = now()
        for d in details:
            blob = {k: (_iso(v) if k in DATE_FIELDS else v) for k, v in d.items() if k != "currency_flags"}
            text = (d.get("description") or "") + "\n" + (d.get("eligibility_text") or "")
            db.q("UPDATE opportunities SET detail=?, text_hash=?, detail_at=?, close_date=COALESCE(?, close_date) WHERE source_record_id=?",
                 (json.dumps(blob), hashlib.sha256(text.encode()).hexdigest()[:16], dstamp, _iso(d.get("close_date")), d["source_record_id"]), write=True)
    finally:
        gg.call_hook = None
    return {"ingest_id": iid, "listed": len(listed), "details_requested": len(want), "details_stored": len(details),
            "details_failed": len(failures), "seconds": round((datetime.now(timezone.utc) - t0).total_seconds(), 1)}


# ------------------------------------------------------------------ read side
def status(db) -> dict:
    n = db.q("SELECT COUNT(*) c FROM opportunities", one=True)["c"]
    d = db.q("SELECT COUNT(*) c FROM opportunities WHERE detail IS NOT NULL", one=True)["c"]
    last = db.q("SELECT MAX(listed_at) m, MAX(detail_at) d FROM opportunities", one=True)
    calls = db.q("SELECT endpoint, COUNT(*) n, SUM(CASE WHEN ok=1 THEN 1 ELSE 0 END) ok, ROUND(AVG(latency_ms)) avg_ms"
                 " FROM api_calls GROUP BY endpoint ORDER BY endpoint")
    return {"opportunities": n, "with_full_text": d, "listed_at": last["m"], "detail_at": last["d"],
            "api_calls": [dict(c) for c in calls]}


def provenance(db) -> dict:
    """Where the opportunity data in a run came from. Shown on the pages and kept with the run."""
    st = status(db)
    stored = st["with_full_text"] > 0
    return {"system": "Grants.gov", "api": "https://api.grants.gov/v1/api (public)",
            "mode": "stored copy" if stored else "live pull",
            "retrieved_at": st["listed_at"] if stored else None,
            "records": st["opportunities"] if stored else None}


def as_of(db):
    r = db.q("SELECT MAX(listed_at) m FROM opportunities", one=True)
    return r["m"] if r else None


def stored_lister(db):
    def lister(statuses=("posted",), timeout=30.0, cache_ttl_minutes=15, **_):
        rows = db.q("SELECT * FROM opportunities")
        wanted = {s.lower() for s in statuses}
        return [{"source_system": r["source_system"], "source_record_id": r["source_record_id"], "number": r["number"] or "",
                 "title": r["title"] or "", "sponsor": r["sponsor"] or "", "agency_code": r["agency_code"] or "",
                 "status": r["status"], "open_date": _date(r["open_date"]), "close_date": _date(r["close_date"]),
                 "cfda": [], "url": r["url"]}
                for r in rows if (r["status"] or "").lower() in wanted]
    return lister


def stored_detailer(db):
    def detailer(record_ids, timeout=30.0, concurrency=8, **_):
        details, failures = [], []
        for rid in record_ids:
            r = db.q("SELECT detail, detail_at FROM opportunities WHERE source_record_id=?", (str(rid),), one=True)
            if not r or not r["detail"]:
                failures.append({"source_record_id": str(rid), "error": "full text not in the stored copy yet"}); continue
            d = json.loads(r["detail"])
            for k in DATE_FIELDS:
                d[k] = _date(d.get(k))
            d["currency_flags"] = _flags(d)
            d["retrieved_at"] = r["detail_at"]
            details.append(d)
        return details, failures
    return detailer


def sources(db, live_lister=None, live_detailer=None):
    """Use the stored copy once it has records; until then, behave exactly as before and pull live."""
    live_lister = live_lister or gg.list_opportunities
    live_detailer = live_detailer or gg.fetch_details
    sl, sd = stored_lister(db), stored_detailer(db)

    def has_store():
        return db.q("SELECT COUNT(*) c FROM opportunities WHERE detail IS NOT NULL", one=True)["c"] > 0

    def lister(*a, **k):
        return sl(*a, **k) if has_store() else live_lister(*a, **k)

    def detailer(*a, **k):
        return sd(*a, **k) if has_store() else live_detailer(*a, **k)
    return lister, detailer
