# Researcher lookup: design (design only, not built)

Status: proposal for the architect and project manager. Nothing here is wired. Contract: `backend/README.md`, section "Researcher lookup (OpenAlex)", on `integration`.
Principle (`docs/FORGE_VISION.md`): does this make managing research easier, or more cumbersome? The lookup is optional. Typing the research areas by hand always works, and always stays one click away.

## Where it sits
Find funding, "A researcher" panel. The name field gains a **Look up public records** button. Everything below happens in that panel; no new page.

## Before anything is searched: the disclosure
Shown next to the button, always visible, plain words:

> Looking up a name sends it to OpenAlex, a public scholarly database, to find public publications.

The same sentence appears once on About (Data and privacy). It is not a pop-up and not hidden in a tooltip.

## The flow
1. **Type a name, press Look up.** The button shows "Looking up…" and is disabled while waiting.
2. **Candidates** (up to 10), one card each: name, institutions, number of works, last active year, top topics, and a button **This is the researcher**. Same-name records are never merged by SIGNAL; if the server says they may be the same person split in two, the page shows its note as written.
3. **Proposed research areas** for the chosen candidate. Each is a row with a tick (on by default), the term in an editable box, how many works it came from, and a **Show the works** disclosure listing each work's title, year and link. Every term can be edited, removed or unticked. **Add an area in the researcher's own words** is always available.
4. **Confirm.** Nothing is searched until the person ticks: *"I have checked these areas and they describe this researcher's established work."* Only then does **Find opportunities** become active. The ticked terms are sent as the research areas.
5. The rest of the flow is unchanged.

```
Researcher
 Name [ Dr. Sample Person          ]  [Look up public records]
 Looking up a name sends it to OpenAlex, a public scholarly database,
 to find public publications.   Or type the research areas yourself below.

 Candidates (2)  <- server note shown as written
 +-------------------------------------------+
 | Sample Person  . Sample University         |
 | 84 works . last active 2026 . photochemistry, flavins
 |                       [This is the researcher]
 +-------------------------------------------+

 Proposed research areas  (edit, remove or add; nothing is searched yet)
  [x] [ photochemistry         ]  12 works  > Show the works
  [x] [ flavin proteins        ]   7 works  > Show the works
  [ ] [ cancer biology         ]   1 work   > Show the works
  + Add an area in the researcher's own words

 [ ] I have checked these areas and they describe this researcher's established work.
 [ Find opportunities ]   (inactive until the box is ticked and one area is kept)
```

## States and the exact texts
Errors arrive as `{detail: {code, message}}`. **Show `message` exactly as the server sends it, in the error block above the field, and keep "type the research areas yourself" available.** Do not reword.

| Situation | Code | Text shown as written |
|---|---|---|
| No researcher matches (status `no_match`) | | "OpenAlex has no researcher matching that name. Check the spelling, try fewer words, or type the research areas yourself." |
| Name too short | `name_too_short` | "Enter at least 2 characters of the researcher's name." |
| Name too long | `name_too_long` | "That name is too long. Enter at most 120 characters." |
| Bad author id | `bad_author_id` | "That is not a valid OpenAlex author id. Search by name and pick a candidate." |
| Our hourly limit | `hourly_limit` | "Too many lookups from this visitor. Please try again in about an hour." |
| Our daily limit | `daily_limit` | "The daily limit for researcher lookups has been reached. Please try again tomorrow." |
| OpenAlex timeout | `upstream_timeout` | "OpenAlex took too long to answer. Please try again in a moment." |
| OpenAlex rate limit | `upstream_rate_limited` | "OpenAlex is limiting requests right now. Please wait a minute and try again." |
| OpenAlex outage | `upstream_unavailable` | "OpenAlex could not be reached or is having an outage. You can continue by typing the research areas yourself." |
| Unreadable answer | `upstream_bad_response` | "OpenAlex returned an answer that could not be read. You can continue by typing the research areas yourself." |

Other states:
- **Empty before searching:** the name box and the typed-areas box both visible; nothing else.
- **Loading:** the button reads "Looking up…"; the result area has `aria-live="polite"` and says "Looking up public records."
- **`single`:** one candidate, still shown as a card and still needs "This is the researcher" (never auto-chosen).
- **`multiple` / `ambiguous`:** all candidates, with the server's note.
- **Expertise `no_works`:** the server's note, and the typed-areas box.

## Design rules this follows
- A person confirms before any search: the tick, and the editable terms.
- Terms are proposals, each with its source works shown. They are OpenAlex's topic names, not the words funders use, so the page says so: *"These are OpenAlex's topic names. Change them to the words you would expect in a funding announcement."*
- Names and author ids are never put in a URL.
- No claim of accuracy. The page does not say the match is right; it says what OpenAlex returned.
- Keyboard: every control reachable in order; the candidate list and the term list are real lists; errors use `role="alert"`; focus moves to the first candidate after a successful search and to the confirm tick after terms load.
- Phone: cards stack; "Show the works" is a native disclosure.

## What needs code (when approved)
Two calls (`POST /api/pi/search`, `GET /api/pi/{id}/expertise`), the panel above in `match.html`, rendering in `app.js`, and one line on About. The Find funding flow after the confirm tick uses the existing `POST /api/runs` with the confirmed terms as the research areas.
