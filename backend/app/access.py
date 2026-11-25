"""Approved-tester access codes (design: docs/BACKEND_DECISIONS.md D7).

A live run needs a code the owner created. A code is shown ONCE, at creation, and stored only as an HMAC keyed from
FORGE_SALT, so the database holds nothing that can be used or guessed. A code is never logged, never put in an error,
never returned again. Each code has its own allowance of live runs, an optional expiry and can be revoked.
"""
import hashlib
import hmac
import os
import re
import secrets
import uuid
from datetime import datetime, timezone

from .db import now

LABEL_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9 _-]{0,59}")       # no '@': a label is not an email or a real name
MESSAGES = {
    "missing": "Live searches are for approved testers. Enter your access code, or look at the recorded example.",
    "invalid": "That access code was not recognised. Check it and try again, or look at the recorded example.",
    "expired": "This access code has expired. Ask the project owner for a new one, or look at the recorded example.",
    "revoked": "This access code is no longer active. Ask the project owner, or look at the recorded example.",
    "allowance_used": "This access code has used all of its live runs. Ask the project owner, or look at the recorded example.",
    "too_many_attempts": "Too many access code attempts from this visitor. Please try again in an hour.",
}


class AccessError(Exception):
    def __init__(self, code):
        self.code, self.status, self.message = code, (429 if code == "too_many_attempts" else 403), MESSAGES[code]
        super().__init__(code)

    def detail(self):
        d = {"code": self.code, "message": self.message}
        if self.status == 403:
            d["recorded_example"] = True
        return d


class NoSalt(Exception):
    pass


def _key() -> bytes:
    salt = os.environ.get("FORGE_SALT", "")
    if not salt:
        raise NoSalt("FORGE_SALT must be set on the server before access codes can be created or checked.")
    return hashlib.sha256(b"fsa-access-code-v1|" + salt.encode()).digest()


def hash_code(code: str) -> str:
    return hmac.new(_key(), code.encode(), hashlib.sha256).hexdigest()


def new_code() -> str:
    return "fsa_" + secrets.token_urlsafe(24)


def iso_expiry(value, default):
    """None/omitted -> the default; 'none' -> no expiry; 'YYYY-MM-DD' means the START of that day, UTC; or a full ISO time."""
    v = default if value is None else value
    if v in (None, "", "none"):
        return None
    try:
        dt = datetime.fromisoformat(v)
    except (TypeError, ValueError):
        raise ValueError("expires_at must be a date like 2026-12-08, a full ISO time, or 'none'")
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).isoformat(timespec="seconds")


def create(db, label, allowance, expires_at, actor) -> dict:
    if not LABEL_RE.fullmatch(label or ""):
        raise ValueError("label: 1 to 60 letters, digits, spaces, - or _ (no '@'); use a label like 'tester 1', never a real name")
    if not isinstance(allowance, int) or isinstance(allowance, bool) or not 1 <= allowance <= 20:
        raise ValueError("allowance must be a whole number from 1 to 20")
    code, cid = new_code(), uuid.uuid4().hex[:12]
    db.q("INSERT INTO access_codes(id,label,code_hash,allowance,expires_at,created_at,created_by) VALUES(?,?,?,?,?,?,?)",
         (cid, label, hash_code(code), allowance, expires_at, now(), actor), write=True)
    return {"id": cid, "code": code, "label": label, "allowance": allowance, "expires_at": expires_at}


def lookup(db, code: str):
    return db.q("SELECT * FROM access_codes WHERE code_hash=?", (hash_code(code),), one=True)


def state(row) -> str:
    """None when usable now, else the error code. Expiry and revocation are checked before the allowance."""
    if row["revoked_at"]:
        return "revoked"
    if row["expires_at"] and row["expires_at"] <= now():
        return "expired"
    if row["runs_used"] >= row["allowance"]:
        return "allowance_used"
    return None


def check(db, code: str) -> dict:
    """Validate a code without spending anything. Raises AccessError; returns the row when usable."""
    if not code:
        raise AccessError("missing")
    row = lookup(db, code)
    if row is None or not hmac.compare_digest(row["code_hash"], hash_code(code)):
        raise AccessError("invalid")
    st = state(row)
    if st:
        raise AccessError(st)
    return row


def claim(db, row) -> bool:
    """Atomically take one run from the allowance. False if it was used up, revoked or expired in the meantime."""
    n = db.execute_count("UPDATE access_codes SET runs_used=runs_used+1, last_used_at=? WHERE id=? AND runs_used<allowance"
                         " AND revoked_at IS NULL AND (expires_at IS NULL OR expires_at>?)", (now(), row["id"], now()))
    return n == 1


def refund(db, code_id) -> None:
    db.execute_count("UPDATE access_codes SET runs_used=runs_used-1 WHERE id=? AND runs_used>0", (code_id,))


def remaining(db, code_id) -> int:
    r = db.q("SELECT allowance-runs_used AS r FROM access_codes WHERE id=?", (code_id,), one=True)
    return max(0, int(r["r"])) if r else 0


def listing(db) -> list:
    rows = db.q("SELECT a.id, a.label, a.allowance, a.runs_used, a.expires_at, a.revoked_at, a.created_at, a.last_used_at,"
                " COUNT(r.id) AS runs, COALESCE(SUM(r.cost_usd), 0) AS cost FROM access_codes a LEFT JOIN runs r ON r.access_code_id=a.id"
                " GROUP BY a.id, a.label, a.allowance, a.runs_used, a.expires_at, a.revoked_at, a.created_at, a.last_used_at ORDER BY a.created_at, a.id")
    out = []
    for r in rows:
        out.append({"id": r["id"], "label": r["label"], "allowance": r["allowance"], "runs_used": r["runs_used"],
                    "remaining": max(0, r["allowance"] - r["runs_used"]), "expires_at": r["expires_at"],
                    "revoked": bool(r["revoked_at"]), "created_at": r["created_at"], "last_used_at": r["last_used_at"],
                    "runs": r["runs"], "cost_usd_estimate": round(float(r["cost"] or 0), 4)})
    return out


def revoke(db, code_id):
    row = db.q("SELECT id, revoked_at FROM access_codes WHERE id=?", (code_id,), one=True)
    if row is None:
        return None
    if not row["revoked_at"]:
        db.q("UPDATE access_codes SET revoked_at=? WHERE id=?", (now(), code_id), write=True)
    return db.q("SELECT revoked_at FROM access_codes WHERE id=?", (code_id,), one=True)["revoked_at"]
