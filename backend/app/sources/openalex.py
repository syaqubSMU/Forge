"""OpenAlex lookup of a researcher (public scholarly index, https://api.openalex.org).

Flow the page follows (nothing is screened until the person confirms):
  1. search_authors(name)       candidates to pick from: institution, works count, citations, top topics
  2. expertise(author_id)       research-area terms drawn from that author's recent public works, each with the
                                works that produced it, so the person can see where every term came from
  3. the person edits and confirms the terms; only then does POST /api/runs use them as `profile.lanes`

Privacy: requests carry a generic client name and only the typed name or the chosen OpenAlex id. No email,
no contact details, no key. Nothing returned here is stored by this module.
"""
import re
from collections import defaultdict
from datetime import date

import httpx

BASE = "https://api.openalex.org"
USER_AGENT = "forge-signal"
ID_RE = re.compile(r"^A\d{4,12}$")
# Topic names too broad to describe anyone's expertise.
GENERIC = {"research", "science", "technology", "study", "studies", "education", "health", "medicine"}


class OpenAlexError(RuntimeError):
    """The scholarly index could not be read, or the request was malformed."""


def _get(path, params, client=None, timeout=20.0):
    try:
        c = client or httpx.Client(headers={"User-Agent": USER_AGENT}, timeout=timeout)
        r = c.get(BASE + path, params=params)
    except httpx.HTTPError as e:
        raise OpenAlexError(f"scholarly index unreachable ({type(e).__name__})")
    if r.status_code != 200:
        raise OpenAlexError(f"scholarly index returned HTTP {r.status_code}")
    try:
        return r.json()
    except ValueError:
        raise OpenAlexError("scholarly index returned an unreadable answer")


def short_id(openalex_id: str) -> str:
    return (openalex_id or "").rstrip("/").rsplit("/", 1)[-1]


def search_authors(name: str, limit: int = 8, client=None) -> list:
    name = " ".join((name or "").split())
    if len(name) < 3 or len(name) > 120:
        raise OpenAlexError("enter a name of 3 to 120 characters")
    j = _get("/authors", {"search": name, "per-page": max(1, min(limit, 15)),
                          "select": "id,display_name,works_count,cited_by_count,last_known_institutions,affiliations,topics"}, client)
    out = []
    for a in j.get("results", []):
        inst = (a.get("last_known_institutions") or [])
        inst_name = inst[0]["display_name"] if inst else None
        if not inst_name and a.get("affiliations"):
            inst_name = a["affiliations"][0]["institution"]["display_name"]     # most recent listed affiliation
        out.append({"openalex_id": short_id(a["id"]), "name": a.get("display_name", ""), "institution": inst_name,
                    "works_count": a.get("works_count", 0), "cited_by_count": a.get("cited_by_count", 0),
                    "top_topics": [t["display_name"] for t in (a.get("topics") or [])[:3]]})
    return out


def expertise(author_id: str, years: int = 6, max_works: int = 50, max_terms: int = 12, client=None, today=None) -> dict:
    """Terms from the author's most recent works. A term's strength is how many of those works carry it."""
    if not ID_RE.match(author_id or ""):
        raise OpenAlexError("not an OpenAlex author id")
    since = (today or date.today()).year - years
    j = _get("/works", {"filter": f"author.id:{author_id},from_publication_date:{since}-01-01",
                        "sort": "publication_date:desc", "per-page": max(1, min(max_works, 100)),
                        "select": "id,title,publication_year,doi,topics,keywords"}, client)
    works = j.get("results", [])
    support = defaultdict(list)
    for w in works:
        names = {t["display_name"] for t in (w.get("topics") or [])[:3]} | {k["display_name"] for k in (w.get("keywords") or [])[:5]}
        ref = {"title": w.get("title") or "(untitled)", "year": w.get("publication_year"), "url": w.get("doi") or w.get("id")}
        for n in names:
            if n and n.lower() not in GENERIC:
                support[n].append(ref)
    ranked = sorted(support.items(), key=lambda kv: (-len(kv[1]), kv[0].lower()))[:max_terms]
    return {"openalex_id": author_id, "works_considered": len(works), "from_year": since,
            "terms": [{"term": t, "work_count": len(ws), "works": ws[:5]} for t, ws in ranked],
            "source": {"system": "OpenAlex", "api": BASE, "note": "Terms come from the titles' assigned topics and keywords; the person confirms or edits them."}}
