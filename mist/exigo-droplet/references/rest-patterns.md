# REST: SDK client, and calls outside the SDK

## SDK client

```ts
import { createExigoRestClient } from "@fluid-app/exigo-connection-sdk/rest";
import type { ExigoEgressProxy } from "@fluid-app/exigo-connection-sdk/sql";

export function buildRestClient(creds: {
  baseUrl: string;
  username: string;
  password: string;
  company: string;
  egressProxy?: ExigoEgressProxy;
}) {
  const { egressProxy, ...rest } = creds;
  return createExigoRestClient(rest, egressProxy ? { egressProxy } : {});
}

const client = buildRestClient(creds);
const data = await client.get<unknown>("customers", { query: { customerID: 123 } });
```

- `baseUrl` is the tenant host, `https://<tenant>.exigo.com` or with `/3.0`; the client adds `/3.0` and refuses any other version segment. Paths are relative and must not start with a version or be absolute URLs.
- Basic auth is `username@company`, so `company` is required. A bare username is rejected as bad credentials.
- `egressProxy` needs `undici` installed and is loaded only when set. Default timeout 15s (`timeoutMs` per client or per call).
- Methods: `get`, `post`, `put`, `patch`, `delete`, `request`. Path placeholders: `client.get("customers/{id}", { params: { id } })`.
- Errors: `ExigoAuthError` (401/403), `ExigoApiError` (other non-2xx, or a 2xx with a non-JSON body; carries `status` and a redacted `bodySnippet`), `ExigoTimeoutError`, `ExigoConnectionError`, `ExigoProxyError`. Translate with the same `asConnectionError` order as SQL, adding an `ExigoApiError` branch.
- A REST 401 containing `IP <addr> not allowed` is the tenant's IP allowlist, not a password problem.

## Calls outside the SDK (SOAP, API-root probes)

Anything the SDK client cannot make must still leave from the allowlisted IP. Build an undici `ProxyAgent` the way the SDK does and cache it per proxy origin and token.

```ts
import type { ExigoEgressProxy } from "@fluid-app/exigo-connection-sdk/sql";

const globalForProxy = globalThis as unknown as {
  exigoProxyTransports?: Map<string, Promise<{ fetch: typeof fetch; dispatcher: unknown }>>;
};
const transports = (globalForProxy.exigoProxyTransports ??= new Map());

function transportFor(proxy: ExigoEgressProxy) {
  const token = proxy.token.replace(/^\s*Bearer\s+/i, "").trim();
  const uri = new URL(proxy.url.trim()).origin;
  const key = `${uri}\n${token}`;
  let transport = transports.get(key);
  if (!transport) {
    transport = import("undici").then((undici) => ({
      fetch: undici.fetch as unknown as typeof fetch,
      dispatcher: new undici.ProxyAgent({ uri, token: `Bearer ${token}` }),
    }));
    transport.catch(() => transports.delete(key));
    transports.set(key, transport);
  }
  return transport;
}

export async function exigoFetch(
  input: string | URL,
  init: RequestInit,
  proxy: ExigoEgressProxy | undefined,
): Promise<Response> {
  if (!proxy) return fetch(input, init);
  const transport = await transportFor(proxy);
  return transport.fetch(input, { ...init, dispatcher: transport.dispatcher } as RequestInit);
}
```

`globalThis` caching stops dev hot-reload from leaking agents and reuses open tunnels. Never fall back to a plain `fetch` when a proxy is configured: `exigoFetch` takes `proxy` from the same `resolveEgressProxy` call as everything else, so its absence means local development only.
