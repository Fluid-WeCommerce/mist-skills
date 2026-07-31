# Connecting to Wisp, and what to do when it answers nothing

## Connect

Wisp exposes its corpus over an MCP server on the merchant's own Wisp deployment, authenticated with
a **per-company secret token**:

```bash
claude mcp add --transport http wisp \
  https://<mist-host>.wecommerce.dev/api/mcp \
  --header "Authorization: Bearer wmcp_..."
```

Mint the token in **Fluid admin → Droplets → Wisp → MCP access**. Three things about it:

- It is **shown once**. Only a hash is stored, so a lost token is re-minted, never recovered.
- It is **not the write key**. The write key is public, sits in the storefront's page source, and can
  only append data. This one is secret and reads. Never paste one where the other belongs.
- It is **scoped to one company**. The token *is* the tenant — no tool takes a company id, so a token
  can only ever see its own merchant's sessions.

**Never rotate a token to fix a problem.** Rotation invalidates whatever configuration is currently
working. There is no read-only question worth breaking a merchant's setup for.

## When a call fails

| What you see | What it means | What to do |
| --- | --- | --- |
| `401` on every call | Token revoked, mistyped, or belongs to a different company | Re-mint in the droplet panel and re-add the MCP server. Do not retry the same token. |
| `401` after it worked | Someone revoked it, or the merchant reinstalled Wisp | Re-mint. If it keeps happening, something else is revoking tokens — say so rather than minting in a loop. |
| Connection refused / DNS failure | Wrong host, or the Mist is not deployed | Confirm the host from the droplet's embed URL. |
| Tools missing from `tools/list` | Older Wisp deployment than this skill expects | Report which tools you got; work with those, or ask for a redeploy. Do not fabricate a call. |

## When the corpus is empty

This is the important table, because an empty corpus and a healthy-but-quiet storefront look
identical from the outside — and the wrong diagnosis wastes a merchant's afternoon.

Run `signal_stats` and `list_sessions` over the last 7 days first. Then:

| Symptom | Most likely cause | How to confirm | What to tell the merchant |
| --- | --- | --- | --- |
| **Zero sessions, ever** | The pixel is not live on the storefront | The droplet panel's status will say it has never received anything | The install is incomplete — point them at `mist/wisp-install`, specifically the Global Embed step |
| **Sessions stopped abruptly** | Write key rotated out from under a deployed snippet, or the embed was deactivated | Panel shows chunks arriving but rejected, or nothing at all since a datestamp | Re-copy the snippet from *Install the pixel* and update the Global Embed |
| **Zero sessions, recording switched off** | The merchant turned it off | The settings page shows recording disabled | Not a fault — ask whether they want it back on |
| **Sessions exist but none in your window** | Wrong window, or retention already reaped it | Widen the window and re-run | Say which window actually has data |
| **A trickle far below their traffic** | Sampling rate is below 1 | Check the sampling setting | Rates remain valid; absolute counts are a fraction — say so before quoting any total |

**In every one of these cases: stop and say so.** Do not answer the merchant's question from the
product documentation, from general ecommerce knowledge, or from anything other than their own
sessions. An answer Wisp did not earn is worse than no answer, because it is indistinguishable from
one that Wisp did earn.

## When the corpus is small

Single-digit sessions is an anecdote. Say that *before* doing the analysis, not after — the merchant
should decide whether to spend the time.

A workable bar:

- **< 10 sessions** in the window: report what you see as observations about specific sessions, named
  as such. No rates, no trends, no comparisons.
- **10–50**: rates are indicative. Always state the denominator inline ("7 of 41 sessions"), never a
  bare percentage.
- **> 50**: rates and period comparisons are reasonable. Still attach denominators.

For any comparison between two windows, both windows need to clear the bar. A confident-sounding
"up 40% week over week" computed from 5 sessions against 3 is worse than silence.

## Sanity checks worth running once

- **Does the merchant's traffic roughly match the session count?** An order-of-magnitude gap means
  sampling, a partial install, or bot filtering — find out which before reporting anything.
- **Is there a `degraded` cluster?** Many degraded sessions on one path means that page is tripping
  the recorder's circuit breaker. That is itself a finding — the page is mutating the DOM violently
  enough to be a performance problem for real shoppers.
- **Do the `playerUrl`s actually open?** Spot-check one before you hand a merchant a list. Pageviews
  whose first chunk never arrived cannot be replayed, and a dead link undoes the credibility of the
  whole answer.
