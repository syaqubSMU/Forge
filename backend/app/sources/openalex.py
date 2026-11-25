"""OpenAlex lookup of a researcher (public scholarly index, https://api.openalex.org).

Flow the page follows (nothing is screened until the person confirms):
  1. POST /api/pi/search {"name"}   candidates to pick from: institutions, works count, citations, last active year, topics
  2. GET  /api/pi/{id}/expertise    PROPOSED research-area terms from that author's recent public works, each with the
                                    works that produced it; the person edits or removes terms
  3. the person confirms; only then does POST /api/runs use the terms as `profile.lanes`

Privacy: requests carry a generic client name and only the typed name or the chosen OpenAlex id. No email, no contact
details, no key. The typed name is never logged or stored: the call log keeps only the endpoint, status, latency and, for a name search, its length. Answers are kept
in memory for a few minutes (so repeat lookups do not hit OpenAlex again) and are never written to the database.
"""
import re
import threading
import time
import unicodedata
from collections import defaultdict
from datetime import date

import httpx

BASE = "https://api.openalex.org"
USER_AGENT = "forge-signal"
ID_RE = re.compile(r"^A\d{4,12}$")
# Topic names too broad to describe anyone's expertise.
GENERIC = {"research", "science", "technology", "study", "studies", "education", "health", "medicine"}
NAME_MIN, NAME_MAX = 2, 120

# Error table the front end shows as written: code -> (HTTP status, plain-language text).
ERRORS = {
    "name_too_short": (400, "Enter at least 2 characters of the researcher's name."),
    "name_too_long": (400, "That name is too long. Enter at most 120 characters."),
    "bad_author_id": (400, "That is not a valid OpenAlex author id. Search by name and pick a candidate."),
    "hourly_limit": (429, "Too many lookups from this visitor. Please try again in about an hour."),
    "daily_limit": (429, "The daily limit for researcher lookups has been reached. Please try again tomorrow."),
    "upstream_timeout": (504, "OpenAlex took too long to answer. Please try again in a moment."),
    "upstream_rate_limited": (503, "OpenAlex is limiting requests right now. Please wait a minute and try again."),
    "upstream_unavailable": (502, "OpenAlex could not be reached or is having an outage. You can continue by typing the research areas yourself."),
    "upstream_bad_response": (502, "OpenAlex returned an answer that could not be read. You can continue by typing the research areas yourself."),
}


class OpenAlexError(RuntimeError):
    def __init__(self, code):
        self.code, (self.status, self.message) = code, ERRORS[code]
        super().__init__(self.message)


def clean_name(name) -> str:
    """Drop control and invisible-format characters, collapse spaces, and enforce length. Non-Latin names pass."""
    s = "".join(ch if not unicodedata.category(ch).startswith("C") else " " for ch in str(name or ""))
    s = " ".join(s.split())
    if len(s) < NAME_MIN:
        raise OpenAlexError("name_too_short")
    if len(s) > NAME_MAX:
        raise OpenAlexError("name_too_long")
    return s


def short_id(openalex_id: str) -> str:
    return (openalex_id or "").rstrip("/").rsplit("/", 1)[-1]


class Lookup:
    """One per server process. `client` is injectable for tests; `log(endpoint, params, ok, status, ms, error)` writes the call log."""

    def __init__(self, client=None, log=None, ttl_s=600, max_cache=500, timeout=15.0):
        self.client = client or httpx.Client(headers={"User-Agent": USER_AGENT}, timeout=timeout)
        self.log, self.ttl, self.max_cache = log, ttl_s, max_cache
        self.cache, self._lock = {}, threading.Lock()

    def _get(self, path, params, log_params):
        key = (path, tuple(sorted(params.items())))
        now = time.time()
        with self._lock:
            hit = self.cache.get(key)
            if hit and now - hit[0] < self.ttl:
                return hit[1], True
        t = time.time(); status = None; err = None
        try:
            r = self.client.get(BASE + path, params=params)
            status = r.status_code
            if status == 429:
                raise OpenAlexError("upstream_rate_limited")
            if status != 200:
                raise OpenAlexError("upstream_unavailable")
            try:
                data = r.json()
            except ValueError:
                raise OpenAlexError("upstream_bad_response")
        except OpenAlexError as e:
            err = e.code; raise
        except httpx.TimeoutException:
            err = "upstream_timeout"; raise OpenAlexError("upstream_timeout")
        except httpx.HTTPError as e:
            err = "upstream_unavailable"; raise OpenAlexError("upstream_unavailable")
        finally:
            if self.log:
                self.log(path, log_params, err is None, status, int((time.time() - t) * 1000), err)
        with self._lock:
            if len(self.cache) >= self.max_cache:
                self.cache.pop(next(iter(self.cache)))
            self.cache[key] = (now, data)
        return data, False

    def search(self, name: str, limit: int = 10) -> dict:
        name = clean_name(name)
        j, cached = self._get("/authors", {"search": name, "per-page": max(1, min(limit, 10)),
                              "select": "id,display_name,works_count,cited_by_count,last_known_institutions,affiliations,topics,counts_by_year"},
                              {"name_length": len(name)})      # length only: a bare hash of a name can be checked by anyone with a guess
        out = []
        for a in j.get("results", [])[:10]:
            insts = []
            for i in (a.get("last_known_institutions") or []):
                insts.append(i.get("display_name"))
            for af in (a.get("affiliations") or [])[:8]:
                insts.append((af.get("institution") or {}).get("display_name"))
            insts = list(dict.fromkeys(x for x in insts if x))[:5]
            years = [c["year"] for c in (a.get("counts_by_year") or []) if c.get("works_count")]
            out.append({"openalex_id": short_id(a.get("id")), "name": a.get("display_name", ""), "institutions": insts,
                        "works_count": a.get("works_count", 0), "cited_by_count": a.get("cited_by_count", 0),
                        "last_active_year": max(years) if years else None,
                        "top_topics": [t["display_name"] for t in (a.get("topics") or [])[:3]]})
        norm = defaultdict(int)
        for c in out:
            norm[re.sub(r"[\W_]+", "", c["name"].casefold())] += 1       # Unicode letters, so non-Latin names compare correctly
        if not out:
            status, note = "no_match", "OpenAlex has no researcher matching that name. Check the spelling, try fewer words, or type the research areas yourself."
        elif max(norm.values()) > 1:
            status, note = "ambiguous", ("Several records have the same or a very similar name. They may be one person split into separate "
                                         "records, or different people. They are shown separately and not merged: pick the one whose institution, "
                                         "topics and recent activity fit, and check the works behind each term in the next step.")
        elif len(out) > 1:
            status, note = "multiple", "More than one researcher matches. Pick the one whose institution and topics fit."
        else:
            status, note = "single", "One researcher matches. Check the institution and topics before continuing."
        return {"status": status, "note": note, "candidates": out, "source": {"system": "OpenAlex", "api": BASE}}

    def expertise(self, author_id: str, years: int = 6, max_works: int = 50, max_terms: int = 12, today=None) -> dict:
        """PROPOSED terms from the author's most recent works. A term's strength is how many of those works carry it."""
        if not ID_RE.fullmatch(author_id or ""):
            raise OpenAlexError("bad_author_id")
        since = (today or date.today()).year - years
        j, _ = self._get("/works", {"filter": f"author.id:{author_id},from_publication_date:{since}-01-01",
                                    "sort": "publication_date:desc", "per-page": max(1, min(max_works, 100)),
                                    "select": "id,title,publication_year,doi,topics,keywords"},
                         {})      # nothing about who was looked up is logged
        works = j.get("results", [])
        support = defaultdict(list)
        for w in works:
            names = {t["display_name"] for t in (w.get("topics") or [])[:3]} | {k["display_name"] for k in (w.get("keywords") or [])[:5]}
            ref = {"title": w.get("title") or "(untitled)", "year": w.get("publication_year"), "url": w.get("doi") or w.get("id")}
            for n in names:
                if n and n.lower() not in GENERIC:
                    support[n].append(ref)
        ranked = sorted(support.items(), key=lambda kv: (-len(kv[1]), kv[0].lower()))[:max_terms]
        note = ("No works from the last %d years were found for this record. Choose another candidate or type the research areas yourself." % years
                if not works else
                "These terms are proposed from public works only (topics and keywords OpenAlex assigns). Edit or remove any term before continuing.")
        return {"openalex_id": author_id, "works_considered": len(works), "from_year": since, "status": "ok" if works else "no_works",
                "note": note,
                "terms": [{"term": t, "work_count": len(ws), "works": ws[:5], "proposed": True} for t, ws in ranked],
                "source": {"system": "OpenAlex", "api": BASE}}
