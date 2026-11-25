"""Live Grants.gov pull (PRD FR-5). No stored opportunity index (hard rule 1):
the list is held in this process's memory for a short TTL and never written to the database.

Measured behaviour of the public API (2026-11-23), which this module is built around:
  * search2 keyword matching is too weak for narrow research terms ("photoreceptor" -> 0 hits,
    "chemistry" -> 47), and search hits carry NO synopsis text. So we do not search by keyword:
    we page the whole corpus (790 posted + 588 forecasted in ~1.4s) and filter in plain code.
  * fetchOpportunity returns the real text and takes ~0.2-0.4s, so details are fetched
    concurrently for a bounded shortlist only.
"""
import html
import re
import threading
import time
from datetime import date, datetime

import httpx

BASE = "https://api.grants.gov/v1/api"
PAGE_ROWS = 500
USER_AGENT = "ForgeSignal/0.2 (university research-development pilot)"   # no personal details

_cache: dict = {}
call_hook = None      # optional callable(endpoint, params, ok, http_status, latency_ms, error); set by the ingest job
_cache_lock = threading.Lock()


class SourceError(RuntimeError):
    """The source could not be read. Never silently swallowed: the run records it."""


# ---------------------------------------------------------------- parsing (plain code, hard rule 6)
def parse_list_date(value):
    """search2 hits use MM/DD/YYYY."""
    try:
        return datetime.strptime(str(value).strip(), "%m/%d/%Y").date()
    except (ValueError, TypeError):
        return None


def parse_detail_date(value):
    """fetchOpportunity uses e.g. 'Jan 07, 2028 12:00:00 AM EST'."""
    s = str(value or "").strip()
    if not s:
        return None
    m = re.match(r"([A-Za-z]{3})\s+(\d{1,2}),\s*(\d{4})", s)
    if not m:
        return None
    try:
        return datetime.strptime(f"{m.group(1)} {m.group(2)} {m.group(3)}", "%b %d %Y").date()
    except ValueError:
        return None


def clean_text(value) -> str:
    """Strip HTML from sponsor text. The model quotes this text and the validator checks
    quotes against the same cleaned string, so the two always agree."""
    s = html.unescape(re.sub(r"<[^>]+>", " ", str(value or "")))
    return re.sub(r"[ \t ]+", " ", s).strip()


def parse_money(value):
    """Grants.gov sends 'none', '' or a numeric string for award amounts. Anything that is not a
    positive number is unstated, and stays unstated: it is never turned into zero (PRD FR-13)."""
    try:
        n = int(float(str(value).strip()))
    except (TypeError, ValueError):
        return None
    return n if n > 0 else None


def days_until(d, today=None):
    return None if d is None else (d - (today or date.today())).days


# ---------------------------------------------------------------- HTTP
def _log(endpoint, body, ok, status, t0, error=None):
    hook = call_hook
    if hook:
        try:
            params = {k: v for k, v in body.items() if k in ("rows", "startRecordNum", "oppStatuses", "opportunityId")}
            hook(endpoint, params, ok, status, int((time.time() - t0) * 1000), error)
        except Exception:
            pass                                 # logging must never break a pull


def _post(client: httpx.Client, endpoint: str, body: dict) -> dict:
    last = None
    for attempt in range(3):
        t0, status = time.time(), None
        try:
            r = client.post(f"{BASE}/{endpoint}", json=body)
            status = r.status_code
            if r.status_code >= 500:
                last = SourceError(f"{endpoint}: HTTP {r.status_code}")
            else:
                r.raise_for_status()
                data = r.json()
                if data.get("errorcode") not in (0, None):
                    raise SourceError(f"{endpoint}: {data.get('msg') or data.get('errorcode')}")
                _log(endpoint, body, True, status, t0)
                return data.get("data") or {}
        except httpx.HTTPError as e:
            last = SourceError(f"{endpoint}: {type(e).__name__}")
        except SourceError as e:
            _log(endpoint, body, False, status, t0, str(e)[:200]); raise
        _log(endpoint, body, False, status, t0, str(last)[:200])
        time.sleep(0.4 * (2 ** attempt))      # backoff; fair use
    raise last or SourceError(f"{endpoint}: failed")


def _client(timeout: float) -> httpx.Client:
    return httpx.Client(timeout=timeout, headers={"User-Agent": USER_AGENT, "Content-Type": "application/json"})


# ---------------------------------------------------------------- list
def _normalize_hit(h: dict) -> dict:
    return {
        "source_system": "Grants.gov",
        "source_record_id": str(h.get("id", "")),
        "number": h.get("number") or "",
        "title": h.get("title") or "",
        "sponsor": h.get("agency") or h.get("agencyCode") or "",
        "agency_code": h.get("agencyCode") or "",
        "status": h.get("oppStatus") or "",
        "open_date": parse_list_date(h.get("openDate")),
        "close_date": parse_list_date(h.get("closeDate")),
        "cfda": list(h.get("cfdaList") or []),
        "url": f"https://www.grants.gov/search-results-detail/{h.get('id')}",
    }


def list_opportunities(statuses=("posted",), timeout=30.0, cache_ttl_minutes=15, max_pages=20) -> list:
    """Page the whole corpus. Cached in memory only, for cache_ttl_minutes."""
    key = tuple(sorted(statuses))
    with _cache_lock:
        hit = _cache.get(key)
        if hit and time.time() - hit[0] < cache_ttl_minutes * 60:
            return hit[1]
    out, seen = [], set()
    with _client(timeout) as client:
        for status in key:
            start = 0
            for _ in range(max_pages):
                data = _post(client, "search2", {"rows": PAGE_ROWS, "startRecordNum": start,
                                                 "keyword": "", "oppStatuses": status})
                hits = data.get("oppHits") or []
                for h in hits:
                    rec = _normalize_hit(h)
                    if rec["source_record_id"] and rec["source_record_id"] not in seen:
                        seen.add(rec["source_record_id"]); out.append(rec)
                start += len(hits)
                if not hits or start >= int(data.get("hitCount") or 0):
                    break
    with _cache_lock:
        _cache[key] = (time.time(), out)
    return out


def clear_cache():
    with _cache_lock:
        _cache.clear()


# ---------------------------------------------------------------- detail
def _normalize_detail(d: dict, record_id: str) -> dict:
    syn = d.get("synopsis") or {}
    archive = parse_detail_date(syn.get("archiveDate"))
    related = [str(r.get("id")) for r in (d.get("relatedOpps") or []) if r.get("id")]
    flags = []
    if archive and archive <= date.today():
        flags.append("Archived on the sponsor site")
    if related:
        flags.append("Sponsor lists a related or replacement posting")
    return {
        "source_record_id": record_id,
        "number": d.get("opportunityNumber") or "",
        "title": d.get("opportunityTitle") or "",
        "sponsor": (syn.get("agencyName") or "").strip(),
        "description": clean_text(syn.get("synopsisDesc")),
        "eligibility_text": clean_text(syn.get("applicantEligibilityDesc")),
        "applicant_types": [t.get("description", "") for t in (syn.get("applicantTypes") or [])],
        "close_date": parse_detail_date(syn.get("responseDate")),
        "posting_date": parse_detail_date(syn.get("postingDate")),
        "archive_date": archive,
        "last_updated": parse_detail_date(syn.get("lastUpdatedDate")),
        "award_floor": parse_money(syn.get("awardFloor")),
        "award_ceiling": parse_money(syn.get("awardCeiling")),
        "cost_sharing": syn.get("costSharing"),
        "related_opportunity_ids": related,
        "currency_flags": flags,                  # FR-9: never inferred, read from the sponsor record
        "url": f"https://www.grants.gov/search-results-detail/{record_id}",
    }


def fetch_detail(record_id, timeout=30.0) -> dict:
    with _client(timeout) as client:
        data = _post(client, "fetchOpportunity", {"opportunityId": int(record_id)})
    return _normalize_detail(data, str(record_id))


def fetch_details(record_ids, timeout=30.0, concurrency=8) -> tuple:
    """Return (details, failures). A failure is recorded, never silently dropped."""
    from concurrent.futures import ThreadPoolExecutor
    details, failures = [], []

    def one(rid):
        try:
            return ("ok", fetch_detail(rid, timeout))
        except (SourceError, ValueError, TypeError) as e:
            return ("err", {"source_record_id": str(rid), "error": str(e)})

    with ThreadPoolExecutor(max_workers=max(1, concurrency)) as pool:
        for kind, value in pool.map(one, list(record_ids)):
            (details if kind == "ok" else failures).append(value)
    return details, failures


# ---------------------------------------------------------------- shortlist (plain code)
def shortlist(records, horizon_months=3, include_undated=False, limit=250, today=None) -> list:
    """Filter by the deadline window. Sorted by nearest deadline. No scoring here."""
    today = today or date.today()
    horizon_days = int(round(horizon_months * 30.44))
    keep = []
    for r in records:
        d = days_until(r.get("close_date"), today)
        if d is None:
            if include_undated:
                keep.append((10 ** 6, r))
            continue
        if 0 <= d <= horizon_days:
            keep.append((d, r))
    keep.sort(key=lambda x: (x[0], x[1].get("source_record_id", "")))
    return [r for _, r in (keep if limit is None else keep[:limit])]
