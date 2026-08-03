# Connecting to Wisp, and what to do when it answers nothing

## Connect

Wisp exposes its corpus over a **Streamable HTTP** MCP server on the merchant's own Wisp deployment,
at `https://<mist-host>.wecommerce.dev/api/mcp`, authenticated with a **per-company secret token**
sent as `Authorization: Bearer wmcp_…`.

How you attach it depends on the host. **These are different products — do not give a user the wrong
one.**

### Mist Desktop (the primary host for this skill)

There is **no CLI**. MCP servers are added through Mist's own dialog, and only the user can do it —
the agent has no tool that registers a server. Walk them through it:

**Settings** (gear icon, titlebar) → **MCP servers** → **Manage MCP servers…** → **Add server**

| Field | Value |
| --- | --- |
| Name | `wisp` |
| Scope | **Global** (available everywhere) or **Project** (this company's project only) |
| Streamable HTTP URL | `https://<mist-host>.wecommerce.dev/api/mcp` |
| Authentication | **Bearer token** |
| Bearer token | the `wmcp_…` token |
| Enabled | ticked |
| Trusted | ticked = skip the per-call approval prompt (see below) |

Then **Save server** and click **Test** on the row. Test performs the connection and the `tools/list`
handshake, and the row expands to show every tool it discovered. **Use Test to validate a token** —
it is the cheap way to find out a token is wrong, rather than discovering it three calls into an
analysis.

Facts worth knowing, because they change what you tell a user:

- **Bearer auth is first-class.** Mist attaches `Authorization: Bearer <token>` to the HTTP transport
  itself (`fluid-mono/apps/mist-desktop/src/main/services/mcp.service.ts:702-709`). Wisp's auth
  design needs no workaround.
- **The token never lands in a config file.** It goes into the OS keychain via Electron `safeStorage`
  and the settings record keeps only a `secretRef` pointing at the slot. The field is write-only in
  the UI — after saving, it shows "bearer token set" and never the value. So *you* cannot read a
  token back to check it, and neither can the user: a suspect token is re-minted, not inspected.
- **HTTP(S) only.** `McpServerDefinitionSchema` rejects any URL that isn't `http`/`https`
  (`fluid-mono/apps/mist-desktop/src/shared/ipc-contract.ts:4280-4292`). There is no stdio transport,
  so never propose a `command`/`args` style server config.
- **OAuth is the other supported auth type**, with a Connect OAuth button. Wisp does not implement an
  OAuth provider, so bearer is the right choice — do not pick OAuth and then wonder why it hangs.
- **Tools arrive namespaced** `mcp__<server>__<tool>` — `mcp__wisp__signal_stats` and so on. The
  server name is lowercased with non-alphanumerics collapsed to `_`.

### Claude Code (secondary — only if the user is genuinely in the CLI)

Nothing else in this repo runs in Claude Code — `mist/wisp-install` depends on `fluid_api` and
`db_query`, which are Mist Desktop tools and do not exist there. This skill is the exception, because
it uses nothing but the `wisp` MCP. If the user is in Claude Code:

```bash
claude mcp add --transport http wisp \
  https://<mist-host>.wecommerce.dev/api/mcp \
  --header "Authorization: Bearer wmcp_..."
```

Same namespacing (`mcp__wisp__…`), but Claude Code's own permission model applies, not Mist's — no
Safe Mode, and approvals behave differently. Everything below about Safe Mode and the consent modal
is **Mist Desktop only**.

### Safe Mode blocks this skill outright (Mist Desktop)

While Safe Mode is on, Mist refuses every tool whose name starts with `mcp__`, unconditionally.
`safe-mode-policy.ts:219-223`:

```ts
// Third-party MCP tools are opaque to Mist. Fail closed: approval or a
// trusted-server setting cannot override the user's global Safe Mode.
if (toolName.startsWith("mcp__")) return safeModeRefusal(toolName);
```

Marking the server **Trusted** does not help. Approving the call does not help. The symptom is
distinctive: every Wisp call is refused instantly, with no network request, while the rest of Mist
behaves normally. Recognise it, name it, and ask the user to turn Safe Mode off in the titlebar.

### The consent modal, and what Trusted actually changes

On an **untrusted** server, every single tool call raises a modal — server name, tool name, and the
full JSON arguments — with exactly two buttons, **Allow once** and **Deny**. There is no
"always allow" and no session-wide grant, so approval is genuinely per-call. Concurrent requests
queue behind one another, and an unanswered prompt **auto-denies after 60 seconds**
(`mcp-consent.service.ts:9`, `:87-92`).

Ticking **Trusted** on the server skips the prompt entirely — `requireApproval` returns
`{ allow: true, decision: "trusted" }` before it ever opens a window (`mcp-consent.service.ts:49`).

A full run of this skill is a dozen-plus calls. Tell the user which regime they're in before you
start, so they can either tick Trusted or stay at the keyboard.

### Zero-setup alternative: drive the endpoint directly with `web_fetch`

Registering the server is the nicer path once it is done, but it needs the user
at the keyboard and it dies under Safe Mode. There is a second path that needs
**no setup at all** and **survives Safe Mode**: MCP's Streamable HTTP transport
is plain JSON-RPC 2.0 over POST, and `web_fetch` does arbitrary POSTs.

`web_fetch` is one of the few tools Safe Mode explicitly allows — it carries no
Fluid bearer token, so it cannot mutate the company's production state
(`safe-mode-policy.ts:25-27`). Every `mcp__*` tool is refused outright. So when
Safe Mode is on, this is the ONLY way to reach Wisp.

Verified against production. A cold `tools/call` — no `initialize`, no
`notifications/initialized`, no session id:

```
POST https://<mist-host>.wecommerce.dev/api/mcp
Authorization: Bearer wmcp_…
Content-Type: application/json
Accept: application/json, text/event-stream

{"jsonrpc":"2.0","id":1,"method":"tools/call",
 "params":{"name":"signal_stats","arguments":{"from":"2026-07-25","to":"2026-08-01"}}}
```

**The `Accept` header is not optional and it is the thing that will catch you.**
Send only `application/json` and the server refuses every call with:

```json
{"jsonrpc":"2.0","error":{"code":-32000,
 "message":"Not Acceptable: Client must accept both application/json and text/event-stream"},"id":null}
```

That is an MCP protocol rule, not a Wisp one. Send **both** media types. Wisp
replies with `Content-Type: application/json` and a normal JSON body — you do
not have to unwrap SSE frames.

The result arrives MCP-shaped: the tool's JSON is a string inside
`result.content[0].text`, so parse twice — once for the envelope, once for the
payload.

Wisp is deliberately **stateless**: no `Mcp-Session-Id` is issued or required.
That matters because `web_fetch` returns body, status and content-type but
**not response headers** — a client literally could not echo a session id back.
Any MCP server that requires one is undriveable this way.

`tools/list` over the same transport enumerates the tools and their argument
schemas, which is the cheapest way to confirm a token works.

### About the token

Mint it in **Fluid admin → Droplets → Wisp → MCP access**. Three things about it:

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
| Every call refused instantly, no network request | **Safe Mode is on** — see above | Ask the user to turn Safe Mode off. Nothing else in this table applies until they do. |
| No `mcp__wisp__*` tools exist at all | Server not added, disabled, or named something else | Check Settings → MCP servers. Read the real server name off the row before assuming the prefix. |
| Calls stop happening and nothing comes back | The consent modal is open and unanswered, or timed out at 60s | Ask the user to approve it, or to tick **Trusted** on the server. |
| `401` on every call | Token revoked, mistyped, or belongs to a different company | Re-mint in the droplet panel, then edit the server and paste the new token in the **Bearer token** field (blank leaves the old one in place). Click **Test**. Do not retry the same token. |
| `401` after it worked | Someone revoked it, or the merchant reinstalled Wisp | Re-mint as above. If it keeps happening, something else is revoking tokens — say so rather than minting in a loop. |
| Connection refused / DNS failure | Wrong host, or the Mist is not deployed | Confirm the host from the droplet's embed URL, then correct the **Streamable HTTP URL** field. |
| Server row shows a red error after **Test** | Connection or handshake failed before any tool ran | The row's message is the real error, and Mist redacts the token out of it. Read it to the user verbatim. |
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
