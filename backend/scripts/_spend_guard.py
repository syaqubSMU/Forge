"""Shared guard for scripts that call the live model and cost money (project rule: no spend without an explicit flag).
Prints the planned call count and an estimate before anything is spent, and exits unless --yes-spend-money was given.
The estimate is rough: about 3 US cents per judgment call at claude-opus-5-5 list prices ($4 / $20 per million tokens,
as of 2026-11-03), from measured runs. The provider's usage page is the real figure."""
import sys

PER_CALL_USD = 0.03


def guard(flag_given: bool, planned_calls: int, what: str, max_calls: int = None):
    if max_calls:
        print(f"{what}: typically {planned_calls} to {planned_calls + 2} live model calls, at most about {max_calls} (about ${max_calls * PER_CALL_USD:.1f}); typical cost about ${planned_calls * PER_CALL_USD:.2f}")
    else:
        print(f"{what}: planned live model calls about {planned_calls} (retries may add a few); estimated cost about ${planned_calls * PER_CALL_USD:.2f}")
    if not flag_given:
        sys.exit("not run: nothing was spent. Add --yes-spend-money to call the live model (after the project's approvals).")
