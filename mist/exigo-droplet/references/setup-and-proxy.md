# Setup and egress proxy wiring

## Install

```bash
npm install --save-exact @fluid-app/exigo-connection-sdk   # >= 0.1.15 for SQL through the proxy
npm install mssql          # SQL only
npm install -D @types/mssql
npm install undici         # REST through the proxy, or any non-SDK call through it
```

`mssql` is an optional peer (`>=11 <13`), imported on first pool open. `undici` is an optional peer (`>=6 <8`), loaded only when `egressProxy` is set on a REST client. Check the installed SDK before relying on the proxy: `ExigoPoolOptions` in its `/sql` types must list `egressProxy`.

```ts
// next.config.ts
const nextConfig = {
  serverExternalPackages: ["@electric-sql/pglite", "mssql"],
};
```

```ts
// every route that queries
export const runtime = "nodejs";
```

## Entry points

| Import | Provides |
| --- | --- |
| `@fluid-app/exigo-connection-sdk` | errors (`ExigoAuthError`, `ExigoConnectionError`, `ExigoCredentialsError`, `ExigoProxyError`, `ExigoTimeoutError`, `ExigoApiError`), type `ExigoSqlCredentials`, `defineExigoCredentials` |
| `.../sql` | `getExigoPool`, `closeExigoPool`, type `ExigoEgressProxy`, the same errors |
| `.../rest` | `createExigoRestClient`, type `ExigoEgressProxy`, the same errors |

`ExigoEgressProxy` is exported from `/sql` and `/rest`, not the root. A type-only import from `/sql` is erased at build and does not load `mssql`.

## lib/exigo/egress-proxy.ts

```ts
import type { ExigoEgressProxy } from "@fluid-app/exigo-connection-sdk/sql";

export function resolveEgressProxy(
  authToken: string | null | undefined,
): ExigoEgressProxy | undefined {
  const url = process.env.FLUID_EGRESS_PROXY_URL?.trim();
  if (!url) return undefined;

  const token = authToken?.trim();
  if (!token) {
    throw new Error(
      "FLUID_EGRESS_PROXY_URL is set but this installation has no Fluid authentication token. Reinstall the droplet so the token exchange runs again.",
    );
  }
  return { url, token };
}
```

- `undefined` is correct in local development: Fluid withholds the URL from the pulled env because the proxy refuses callers off its own platform.
- Throw, never fall back to direct, when the URL is set without a token. A direct connection from Vercel hangs and reads as "Exigo is down".
- The token is `companies.authenticationToken` for the request's installation (`context.installation.authenticationToken` after `resolveFluidInstallation`). It is already stored; add no new secret.
- The SDK requires an `https` proxy URL (plain `http` only for loopback) and strips an optional `Bearer ` prefix from the token.

## What the proxy is, for the user

- CONNECT-only forward proxy on static Cloud NAT IPs that Exigo tenants allowlist. It tunnels bytes; TLS is end to end between the app and Exigo.
- Auth is the droplet installation token as `Proxy-Authorization: Bearer dit_...`.
- Two Fluid-side gates the droplet cannot fix: the droplet must be admitted (proxy allowlist or Fluid `egress_allowed` grant), and the destination host and port must be on the proxy's allowlist.
- IPv4 only. Token verification is cached about 60s, so a revoked or newly granted droplet takes up to a minute to change behaviour.
