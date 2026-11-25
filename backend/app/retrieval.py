"""Keyword ranking (BM25) for choosing which opportunities are worth sending to the model.

This is a cost control, not a fit judgment: it orders records by how well their words match the researcher's
stated areas, so the model's limited judgments go to the most plausible records. The tier still comes from the
rubric. No embeddings, no model, no network: plain code over the stored text.

BM25 (Robertson and Sparck Jones): score(d, q) = sum over query terms t of
    idf(t) * f(t, d) * (k1 + 1) / (f(t, d) + k1 * (1 - b + b * |d| / avgdl))
with idf(t) = ln(1 + (N - n_t + 0.5) / (n_t + 0.5)). The title is counted TITLE_WEIGHT times because a
title is a short, dense statement of what the program funds.
"""
import math
import re
from collections import Counter

K1, B, TITLE_WEIGHT = 1.5, 0.75, 3

STOP = set("""a about above after all also an and any are as at be been being but by can could do does each for from had has
have how if in into is it its may more most must no not of on one or other our out over per such than that the their them
then there these they this those through to under up upon use used using via was we were what when where which while who
will with within would you your""".split())
# Words that appear in nearly every funding notice; they carry no topical signal.
BOILERPLATE = set("""applicant applicants application applications award awards eligib eligible fund funds funding grant grants
institution institutions program programs project projects proposal proposals research support supports supporting
opportunity opportunities announcement section sec include includes including provide provides request required
require submit submission review reviewed pi investigator investigators""".split())


def stem(w: str) -> str:
    """Light suffix stripping so 'imaging' and 'images', 'tumors' and 'tumor' meet. Deliberately conservative."""
    for suf in ("ization", "ations", "ation", "ingly", "ities", "ness", "ments", "ment", "ings", "ing", "ies", "ied",
                "ity", "ive", "ous", "als", "al", "ed", "es", "s"):
        if w.endswith(suf) and len(w) - len(suf) >= 4:
            w = w[: -len(suf)]
            break
    if w.endswith("y") and len(w) > 4:
        w = w[:-1] + "i"
    return w


# Two-letter capitals that are common words or titles, not topics.
SHORT_STOP = {"us", "uk", "pi", "vs", "dr", "mr", "pm", "am", "ii", "iv", "no", "or", "to", "of", "in", "on", "at", "by", "as", "is", "it", "an"}


def tokens(text: str) -> list:
    """Lower-cased stems. Two-letter words survive only as capitals in the original (AI, ML, EV), so the
    field's own short names are searchable without letting 'of' or 'to' through."""
    out = []
    for raw in re.findall(r"[A-Za-z0-9]+", text or ""):
        w = raw.lower()
        if len(w) < 3 and not (len(w) == 2 and raw.isupper() and w not in SHORT_STOP):
            continue
        if w in STOP or w in BOILERPLATE:
            continue
        out.append(stem(w))
    return out


class BM25:
    """Index a list of (title, body) pairs; `scores(query)` returns one score per document, in order."""

    def __init__(self, docs, k1=K1, b=B, title_weight=TITLE_WEIGHT):
        self.k1, self.b = k1, b
        self.tf, self.len = [], []
        df = Counter()
        for title, body in docs:
            c = Counter(tokens(body))
            for t, n in Counter(tokens(title)).items():
                c[t] += n * title_weight
            self.tf.append(c)
            self.len.append(sum(c.values()))
            df.update(c.keys())
        self.n = len(docs)
        self.avgdl = (sum(self.len) / self.n) if self.n else 0.0
        self.idf = {t: math.log(1 + (self.n - d + 0.5) / (d + 0.5)) for t, d in df.items()}

    def scores(self, query: str) -> list:
        q = Counter(tokens(query))
        out = []
        for tf, dl in zip(self.tf, self.len):
            s = 0.0
            for t, qn in q.items():
                f = tf.get(t)
                if f:
                    s += self.idf[t] * f * (self.k1 + 1) / (f + self.k1 * (1 - self.b + self.b * dl / (self.avgdl or 1)))
            out.append(s)
        return out

    def matched_terms(self, i: int, query: str) -> list:
        return sorted(t for t in set(tokens(query)) if t in self.tf[i])


def query_text(profile: dict) -> str:
    """Only the researcher's research areas. Career stage and positioning rules are not topics."""
    return " ".join(profile.get("lanes") or [])
