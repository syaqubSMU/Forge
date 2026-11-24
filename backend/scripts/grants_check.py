"""Live check against the real Grants.gov API (no model, no key, no cost).
  python scripts/grants_check.py            posted, 3-month horizon
  python scripts/grants_check.py 12 posted forecasted
Run it by hand; it is not part of the test suite."""
import sys, time
sys.path.insert(0, ".")
from app.sources import grants_gov as g

months = float(sys.argv[1]) if len(sys.argv) > 1 else 3
statuses = tuple(sys.argv[2:]) or ("posted",)

t0 = time.time(); listed = g.list_opportunities(statuses, cache_ttl_minutes=0)
print(f"listed {len(listed)} {'/'.join(statuses)} opportunities in {time.time()-t0:.1f}s")
short = g.shortlist(listed, horizon_months=months, limit=10**6)
print(f"{len(short)} close within {months} months; {sum(1 for r in listed if not r['close_date'])} have no close date")
if not short:
    sys.exit("nothing in horizon")
t1 = time.time(); details, failures = g.fetch_details([r["source_record_id"] for r in short[:5]])
print(f"fetched {len(details)} details in {time.time()-t1:.1f}s, {len(failures)} failed")
for d in details[:3]:
    print(f"\n- {d['title'][:70]}\n  {d['sponsor']} | {d['number']} | closes {d['close_date']} "
          f"({g.days_until(d['close_date'])}d) | text {len(d['description'])+len(d['eligibility_text'])} chars"
          f"\n  flags: {d['currency_flags'] or 'none'} | {d['url']}")
