---
name: Exigo SDK + egress proxy
description: Connect a Mist droplet to an Exigo tenant's SQL reporting database and/or REST API with @fluid-app/exigo-connection-sdk, routed through Fluid's egress proxy so the tenant's IP allowlist works from Vercel.
icon: database
category: mist
---

# Goal

Give the droplet in the active Mist app read access to {{company.name}}'s Exigo tenant: the SQL reporting database (eligibility, subscriptions, autoships, point balances) and/or the Exigo REST API. Exigo authorises callers by **source IP**, and Mist apps run on Vercel with rotating egress, so every connection goes through Fluid's egress proxy, a CONNECT-only forward proxy with static IPs the tenant allowlists. TLS stays end to end; the proxy never sees Exigo credentials. Known gap: with the required `trustServerCertificate: true`, nothing proves the far end of the TLS is Exigo (see `setup-and-proxy.md`); say so to the user.

**If the app was created from the Exigo starter, the SDK, proxy, encrypted credentials and test route are already wired with session-token auth; do not add dri-only admin routes.** Use this skill to extend that wiring, not to rebuild it.

Code for each step lives in the references appended below. Business queries stay in the app; the SDK owns connection, auth, pooling and typed errors only.

# Steps

1. **Confirm scope.** Check the project is a Mist (`.mist` at the root) with a droplet attached (`fluid mist attach-droplet`). Ask which Exigo tenant, whether it needs SQL, REST or both, and what data the droplet must read. Eligibility predicates (who counts as active, which statuses qualify, whether an expiry day is inclusive) are business decisions: confirm each with the user, never guess.
2. **Check proxy readiness, which is Fluid-side config the droplet cannot fix.** All three must hold before any connection can work:
   - The droplet is admitted to the proxy (on its droplet allowlist or granted `egress_allowed` in Fluid). Ask Fluid.
   - The tenant's Exigo host and port are on the proxy's destination allowlist. Ask Fluid; it is proxy configuration that Fluid redeploys, not a runtime toggle.
   - The tenant has allowlisted the proxy's static IPs on its Exigo SQL firewall and REST API. Ask the Exigo tenant admin, with the IPs from Fluid.
   Tell the user who to ask for each; do not block the build on them.
3. **Install.** Add `@fluid-app/exigo-connection-sdk` pinned to an exact version (>= 0.1.15; SQL through the proxy does not exist below it), plus `mssql` for SQL and an exact-pinned `undici` 7.x (SDK peer range `>=6 <8`) for REST or non-SDK calls through the proxy. Add `mssql` to `serverExternalPackages` and set `export const runtime = "nodejs"` on every route that queries. Not Edge. See `setup-and-proxy.md`.
4. **Wire the proxy once** in `lib/exigo/egress-proxy.ts`: `resolveEgressProxy(authToken)` returns `{ url, token }` or `undefined`. `FLUID_EGRESS_PROXY_URL` is injected by Fluid into a droplet-attached Mist app and `fluid mist env pull` omits it on purpose; unset means connect directly (local dev). The token is the installation's own `authenticationToken` (`dit_...`) on the `companies` row, so there is no new secret. If the URL is set and the token is missing, **throw**; never fall back to a direct connection.
5. **Store credentials per installation** in the droplet DB, keyed by `ctx.installation.id` (a reinstall means re-entering them), with the password sealed (AES-256-GCM) under a user-managed key created with `fluid mist env set CREDENTIAL_ENCRYPTION_KEY --generate --json`, so the value never passes through you. Add the table to `lib/schema.ts` and the idempotent DDL to `lib/ensure-schema.ts`. See `credentials-and-admin.md`.
6. **Build the data layer.**
   - SQL: one `withPool` that calls `getExigoPool(creds, { connectTimeoutMs: 12_000, requestTimeoutMs: 25_000, egressProxy })`. See `sql-patterns.md`.
   - REST: `createExigoRestClient(creds, { egressProxy })`; use an undici `ProxyAgent` only for calls outside the SDK. See `rest-patterns.md`.
   - One `asConnectionError` translating SDK errors into an app-local error, `ExigoProxyError` branch first.
7. **Probe the schema before writing queries.** Exigo schemas differ per tenant and a wrong column guess costs a deploy. Read `INFORMATION_SCHEMA.COLUMNS` for the tables you need and show the user the columns.
8. **Add the test-connection route** that runs a real representative query and returns counts, never rows. See `test-connection-and-tests.md`.
9. **Test, then ship.** Add the SDK-mocking tests from the same reference, run `npm run typecheck`, `npm run lint` and `npm test`, then `fluid mist push --watch`. Local dev cannot reach Exigo unless your own IP is allowlisted, so the first real check is the test-connection route on the deployed app.

# Rules

- **Exact pin, and check the pool options.** The `/sql` entry re-exporting `ExigoProxyError` does not prove proxy support. A version supports it only if `ExigoPoolOptions` has `egressProxy`.
- **Always `encrypt: true, trustServerCertificate: true`** for SQL. Exigo's Azure SQL certificate does not match the host and the SDK has no default. `encrypt: false` is refused through the proxy.
- **Bound parameters only** (`request.input`). Never interpolate. Validate numeric ids before the query: an `NaN` or empty id bound as Int matches nothing and reads as a confident "no".
- **Never close the pool.** The SDK caches it per host/port/database/user/password and reclaims idle ones.
- **No env-var fallback to shared Exigo credentials.** A fork once nearly connected to another client's Exigo. A missing credential row is an error.
- **Write-only password.** Admin routes return `passwordSet: boolean`, never the value or ciphertext.
- **Session-token auth on every credential route.** The Droplet Bridge is live: every credential read, write and test route verifies the signed Bridge session token on the server (`lib/fluid/session-token.ts`, `lib/fluid/embedded-session.ts`) and answers 401 to a `dri`-only request or to a token whose `sub` is not a store admin (`urn:fluid:store_admin:`); store members get valid tokens too. The `dri` only finds the installation; it is not a credential. Also validate the admin-entered SQL host and REST base URL (DNS hostname only, refuse every IP literal, https for REST, optional allowlist), and keep a stored password only while its target is unchanged.
- **Unreadable is not false.** Throw when Exigo cannot be read so callers hold; return `false` only when Exigo answered no. Do not retry in the hot path.
- **Budget shopper-facing callbacks** with `Promise.race`; the SDK's connect and request timeouts are not a checkout budget.
- **Prefer status columns over next-run or scheduled-date columns** for eligibility. Those are stored at midnight, so `NextRunDate >= GETDATE()` demotes a member on the day their order is due.
- **Identity comes from the server.** Shopper-facing paths take the installation, company and `authToken` only from `resolveFluidInstallation` or the HMAC-verified webhook's installation, never from request body fields.
- **Names only.** Reference env vars by name; never print, log or commit values, and never read `.env*` files.
- **`proxy.ts` at the app root is the Next 16 middleware (CSP), not the Exigo proxy.** Do not confuse them.

# Symptoms

- A REST 401/403 (the SDK reports every one as `ExigoAuthError` with a fixed message and no body) or a SQL connect that silently times out: may be an IP allowlist rejection that looks like bad credentials. Check proxy wiring and the tenant allowlist first; to read the real REST body (`IP ... not allowed`), probe through the raw `exigoFetch` in `rest-patterns.md`.
- `ExigoProxyError` 407: token rejected, reinstall the droplet. 403: droplet or host not on the proxy allowlists, ask Fluid. 502/504: proxy could not reach Exigo, the tenant may not allowlist the proxy IP yet. 503: transient.
- A proxy admission change takes up to ~60s to show (verification cache); a revocation can last 60s plus a 300s stale grace while Fluid is unreachable. The proxy dials IPv4 only and refuses IP-literal destinations.
- REST 200 with an HTML body: the API root serves HTML for any credentials. Treat non-JSON as failure.
