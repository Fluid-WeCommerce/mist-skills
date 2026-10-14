---
name: Exigo SDK + egress proxy
description: Connect a Mist droplet to an Exigo tenant's SQL reporting database and/or REST API with @fluid-app/exigo-connection-sdk, routed through Fluid's egress proxy so the tenant's IP allowlist works from Vercel.
icon: database
category: mist
---

# Goal

Give the droplet in the active Mist app read access to {{company.name}}'s Exigo tenant: the SQL reporting database (eligibility, subscriptions, autoships, point balances) and/or the Exigo REST API. Exigo authorises callers by **source IP**, and Mist apps run on Vercel with rotating egress, so every connection goes through Fluid's egress proxy, a CONNECT-only forward proxy with static IPs the tenant allowlists. TLS stays end to end; the proxy never sees Exigo credentials.

Code for each step lives in the references appended below. Business queries stay in the app; the SDK owns connection, auth, pooling and typed errors only.

# Steps

1. **Confirm scope.** Check the project is a Mist (`.mist` at the root) with a droplet attached (`fluid mist attach-droplet`). Ask which Exigo tenant, whether it needs SQL, REST or both, and what data the droplet must read. Eligibility predicates (who counts as active, which statuses qualify) are business decisions: confirm them with the user, never guess.
2. **Check proxy readiness, which is Fluid-side config the droplet cannot fix.** All three must hold before any connection can work:
   - The droplet is admitted to the proxy (on its droplet allowlist or granted `egress_allowed` in Fluid). Ask Fluid.
   - The tenant's Exigo host and port are on the proxy's destination allowlist. Ask Fluid.
   - The tenant has allowlisted the proxy's static IPs on its Exigo SQL firewall and REST API. Ask the Exigo tenant admin, with the IPs from Fluid.
   Tell the user who to ask for each; do not block the build on them.
3. **Install.** Add `@fluid-app/exigo-connection-sdk` pinned to an exact version (>= 0.1.15; SQL through the proxy does not exist below it), plus `mssql` for SQL and `undici` for REST or non-SDK calls through the proxy. Add `mssql` to `serverExternalPackages` and set `export const runtime = "nodejs"` on every route that queries. Not Edge. See `setup-and-proxy.md`.
4. **Wire the proxy once** in `lib/exigo/egress-proxy.ts`: `resolveEgressProxy(authToken)` returns `{ url, token }` or `undefined`. `FLUID_EGRESS_PROXY_URL` is injected by Fluid into a droplet-attached Mist app and `fluid mist env pull` omits it on purpose; unset means connect directly (local dev). The token is the installation's own `authenticationToken` (`dit_...`) on the `companies` row, so there is no new secret. If the URL is set and the token is missing, **throw**; never fall back to a direct connection.
5. **Store credentials per installation** in the droplet DB, scoped to `companyId`, with the password sealed (AES-256-GCM) under a user-managed key: `fluid mist env set CREDENTIAL_ENCRYPTION_KEY=<value>` (the user supplies the value). Add the table to `lib/schema.ts` and the idempotent DDL to `lib/ensure-schema.ts`. See `credentials-and-admin.md`.
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
- **Write-only password.** Admin routes return `passwordSet: boolean`, never the value or ciphertext. Admin routes authorise on a `dri`, which is a lookup key and not a credential, so validate the admin-entered host (bare hostname; refuse private, loopback and link-local; optional allowlist).
- **Unreadable is not false.** Throw when Exigo cannot be read so callers hold; return `false` only when Exigo answered no. Do not retry in the hot path.
- **Budget shopper-facing callbacks** with `Promise.race`; the SDK's connect and request timeouts are not a checkout budget.
- **Prefer status columns over date columns** for eligibility. Date columns are stored at midnight, so `NextRunDate >= GETDATE()` demotes a member on the day their order is due.
- **Names only.** Reference env vars by name; never print, log or commit values, and never read `.env*` files.
- **`proxy.ts` at the app root is the Next 16 middleware (CSP), not the Exigo proxy.** Do not confuse them.

# Symptoms

- REST 401 `IP <addr> not allowed`, or a SQL connect that silently times out: an IP allowlist rejection that looks like bad credentials. Check proxy wiring and the tenant allowlist before touching the password.
- `ExigoProxyError` 407: token rejected, reinstall the droplet. 403: droplet or host not on the proxy allowlists, ask Fluid. 502/504: proxy could not reach Exigo, the tenant may not allowlist the proxy IP yet. 503: transient.
- A proxy allowlist or admission change takes up to ~60s to show, because the proxy caches token verification. The proxy dials IPv4 only.
- REST 200 with an HTML body: the API root serves HTML for any credentials. Treat non-JSON as failure.
