---
name: Share library freshness
description: Sweep the videos, images, documents and playlists reps share for pieces that are out of date — retired products, past dates, ended offers, missing languages, nobody sharing them — and retire, expire or fix only what you approve.
icon: archive-restore
---

# Goal

Find everything in {{company.name}}'s share library that reps should no longer be sending, as of {{today}}, and clean it up with the user's approval. In direct selling and social selling, the library is what thousands of reps post and text to their contacts. A video for a product that was retired, a flyer with last year's price, or a promotion that ended in August keeps circulating long after the company moved on — and old claims are exactly what self-regulators ask companies to find and pull everywhere, not just where they were spotted. A short, regular sweep is cheaper than chasing it after a customer or regulator does.

# Rules

- **Read first, write only with the user's go-ahead.** The only writes this skill makes are to a library piece: set an expiry date, switch it to draft, turn it off, add tags or fix its title or description. Each happens only after the user approves the list in chat. If a write is refused because the user turned on Ask before making changes, propose the exact title the refusal gives with `human_in_the_loop` (source `"agent"`, a fresh `suggestion_id` `"fluid-api:<random>"`), END YOUR TURN, and after Approve repeat the same call with `approval_id`.
- **Never delete.** Retiring means draft, off or an expiry date, so the piece can come back. Deleting is the user's call, made elsewhere.
- **Never judge claims.** This skill flags dates, products, offers and languages. If a piece's text makes a health, results or income claim, say "needs a claims review" and leave it for the company's compliance owner; the `compliance/compliance-manager` skill is the place for that.
- **Shares are counts, not proof.** A piece nobody shared in 90 days is a candidate, not a verdict; a new piece may simply be new.
- **Talk in plain words.** Name pieces by title and products by name. No ids, paths, codes or JSON in the chat.

# Steps

## 1. Know what is current

- `fluid_api("/api/settings/company_countries", "GET")` for the markets the company sells in and each market's language.
- `fluid_api("/api/v202604/company/products?filter[status]=archived&page[limit]=100", "GET")`, following `meta.pagination.next_cursor` as `page[cursor]`, for every retired product (keep id and title). Do the same with `filter[status]=active` so you can tell a live product from a retired one by title too.

## 2. Pull the library

`fluid_api("/api/v202604/company/media?filter[status]=published&filter[active]=true&page[limit]=100", "GET")`, following `meta.pagination.next_cursor` as `page[cursor]`, up to 20 pages (2,000 pieces). Keep each piece's `id`, `title`, `description`, `media_type`, `kind`, `created_at`, `updated_at`, `publish_at`, `deactivate_at`, `countries` (empty means every market), `languages`, `tags` and `cta`.

Then the same for playlists: `fluid_api("/api/v202604/company/playlists?filter[status]=published&filter[active]=true&page[limit]=100", "GET")`, with their `title`, `updated_at`, `countries`, `languages` and `total_items_count`.

If you stop at the cap, say the sweep covers the most recent 2,000 pieces.

## 3. Check each piece

For each media piece:

1. **Linked products:** `fluid_api("/api/v2025-06/media/<id>/products", "GET")`. Flag **Retired product** when any linked product is archived, and **Points at nothing** when the piece's `cta` link goes to a product page whose product is archived.
2. **Dates and offers in the words:** read `title` and `description` for a date, month, season or year that is already past (for example "Black Friday 2025", "through Oct 31", "Summer kickoff"), an offer word ("% off", "free shipping", "bonus", "limited time", "ends"), or a price. Flag **Past date** when the date is behind {{today}}; flag **Offer to confirm** when there is an offer or price but no date, because only the user knows if it still holds.
3. **No expiry:** a piece flagged in 1 or 2 with `deactivate_at` empty — it will run forever unless someone stops it.
4. **Languages:** for every market whose language is missing from `languages` (and the piece is shown there: `countries` empty or listing that market), flag **Missing language**. Use the show call's `translation_statuses` (`fluid_api("/api/v202604/company/media/<id>", "GET")`) only for the pieces you are about to report.
5. **Nobody shares it:** for pieces older than 90 days, `fluid_api("/api/v202604/company/media/<id>/shares", "GET")`. Flag **Unshared** when `share_stats.total_shares` is 0, or `shares_last_30_days` is 0 and the piece is older than a year. Keep `total_shares` and `unique_sharers` for every flagged piece, so the cleanup starts with what reps still send.
6. **Stale and still shared:** any piece flagged in 1 or 2 whose `shares_last_30_days` is above 0 is **Still circulating** — the top of the report.

For each playlist, read `fluid_api("/api/v202604/company/playlists/<id>", "GET")` and flag it when any of its `library_items` is a piece you flagged in 1 or 2, or when it has no items.

Work through at most 300 pieces per run, newest-shared first; if there are more, say how many are left and offer to continue.

## 4. Report

Lead with one sentence: how many pieces are live, how many are stale, and how many of those reps shared in the last 30 days.

Then one table per group, most-shared first, at most 15 rows each (offer the rest):

| Piece | Why | Shared (30 days / ever) | Markets | Suggested fix |
| ----- | --- | ----------------------- | ------- | ------------- |

Groups, in order: **Still circulating**, **Retired product / Points at nothing**, **Past date**, **Offer to confirm**, **Missing language** (one row per piece, listing the missing languages), **Unshared**, **Playlists**.

Suggested fixes:

- Retired product or past date → switch to draft, or set an expiry date of today.
- Offer to confirm → ask the user whether it still holds; if not, the same as above; if yes, suggest an expiry date that matches the offer.
- Missing language → list for translation (don't translate here).
- Unshared → retire, merge into a stronger piece, or retitle so reps find it.
- Playlist → remove the stale pieces from it, or retire the playlist if nothing current is left.

End with the 3 actions that would matter most, and ask which to apply.

## 5. Apply what the user approves

For each approved piece, one call:

- Retire: `fluid_api("/api/v202604/company/media/<id>", "PATCH", {"medium": {"status": "draft"}})`
- Expire: `fluid_api("/api/v202604/company/media/<id>", "PATCH", {"medium": {"deactivate_at": "<ISO date>"}})`
- Turn off: `fluid_api("/api/v202604/company/media/<id>", "PATCH", {"medium": {"active": false}})`
- Tag for follow-up: `fluid_api("/api/v202604/company/media/<id>", "PATCH", {"medium": {"tags": [<existing tags>, "needs-update"]}})` — always send the existing tags too.
- Fix a title or description the user wrote or approved: the same call with `title` / `description`.

Read each piece back with `fluid_api("/api/v202604/company/media/<id>", "GET")` and confirm the change. Report what changed in one short list, and anything refused with the reason Fluid gave.

## 6. Hand off

Say in one line who should hear about it: if pieces were still circulating, the field should be told what replaced them (the company's field communications owner); if the sweep found claims to review, the compliance owner. Suggest running this sweep monthly, and after every product retirement or price change.
