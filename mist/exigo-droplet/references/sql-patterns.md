# SQL: pool wrapper, errors, query shapes

## lib/exigo/client.ts

```ts
import type { ConnectionPool } from "mssql";
import type { ExigoSqlCredentials } from "@fluid-app/exigo-connection-sdk";
import type { ExigoEgressProxy } from "@fluid-app/exigo-connection-sdk/sql";
import { getExigoPool } from "@fluid-app/exigo-connection-sdk/sql";

export interface ExigoCredentials {
  host: string;
  database: string;
  username: string;
  password: string;
  port?: number;
  egressProxy?: ExigoEgressProxy; // rides with the credentials; undefined means direct
}

const CONNECT_TIMEOUT_MS = 12_000; // a silent hang is usually an IP allowlist
const REQUEST_TIMEOUT_MS = 25_000;

function toSqlCredentials(creds: ExigoCredentials): ExigoSqlCredentials {
  // egressProxy is a pool option, not a credential field: do not spread it in.
  return {
    host: creds.host,
    port: creds.port ?? 1433,
    database: creds.database,
    username: creds.username,
    password: creds.password,
    encrypt: true,
    trustServerCertificate: true, // Exigo's Azure SQL certificate does not match the host
  };
}

export async function withPool<T>(
  creds: ExigoCredentials,
  fn: (pool: ConnectionPool) => Promise<T>,
): Promise<T> {
  try {
    const pool = await getExigoPool(toSqlCredentials(creds), {
      connectTimeoutMs: CONNECT_TIMEOUT_MS,
      requestTimeoutMs: REQUEST_TIMEOUT_MS,
      ...(creds.egressProxy ? { egressProxy: creds.egressProxy } : {}),
    });
    return await fn(pool); // never pool.close(): the SDK caches and reclaims it
  } catch (error) {
    throw asConnectionError(error);
  }
}

export async function query<T extends Record<string, unknown>>(
  creds: ExigoCredentials,
  statement: string,
  bind: (request: ReturnType<ConnectionPool["request"]>, mssql: typeof import("mssql")) => void,
): Promise<T[]> {
  return withPool(creds, async (pool) => {
    const mssql = await import("mssql");
    const request = pool.request();
    bind(request, mssql);
    const result = await request.query<T>(statement);
    return result.recordset ?? [];
  });
}
```

Pool options apply when the pool opens; the SDK keys pools by host, port, database, user and then by password, TLS settings and proxy, so a rotated password gets its own pool.

## Error translation

One app-local error class and one translator. Use the app's own class, not the SDK's same-named one, so routes can key off its identity.

```ts
import {
  ExigoAuthError,
  ExigoCredentialsError,
  ExigoProxyError,
  ExigoTimeoutError,
} from "@fluid-app/exigo-connection-sdk";

export class ExigoConnectionError extends Error {
  constructor(message: string, readonly cause?: unknown) {
    super(message);
    this.name = "ExigoConnectionError";
  }
}

const PROXY_MESSAGES: Record<number, string> = {
  407: "Fluid's egress proxy did not accept this installation's token. Reinstall the droplet.",
  403: "Fluid's egress proxy refused this droplet or this Exigo host. Ask Fluid to add them to its allowlists.",
  502: "Fluid's egress proxy could not reach the Exigo host. Check host and port; the tenant may not allowlist the proxy IP yet.",
  504: "Fluid's egress proxy timed out reaching the Exigo host. The tenant may not allowlist the proxy IP yet.",
  503: "Fluid's egress proxy is unavailable or at capacity. Transient; retry later.",
};

export function asConnectionError(error: unknown): ExigoConnectionError {
  if (error instanceof ExigoConnectionError) return error;
  // FIRST: ExigoProxyError extends the SDK's connection error and would otherwise
  // be reported as "could not reach Exigo" when the refusal came from Fluid's proxy.
  if (error instanceof ExigoProxyError) {
    return new ExigoConnectionError(
      PROXY_MESSAGES[error.status] ?? `Fluid's egress proxy refused the connection (HTTP ${error.status}).`,
      error,
    );
  }
  if (error instanceof ExigoTimeoutError) {
    return new ExigoConnectionError(
      "Timed out reaching the Exigo SQL Server. Usually an IP allowlist or a wrong host or port, not a bad password.",
      error,
    );
  }
  if (error instanceof ExigoAuthError) {
    return new ExigoConnectionError("Exigo rejected the username or password.", error);
  }
  if (error instanceof ExigoCredentialsError) {
    return new ExigoConnectionError(`Exigo connection is not configured correctly: ${error.message}`, error);
  }
  const raw = error instanceof Error ? error.message : String(error);
  if (/ETIMEOUT|ETIMEDOUT|timeout/i.test(raw)) return new ExigoConnectionError("Timed out reaching the Exigo SQL Server.", error);
  if (/ELOGIN|Login failed/i.test(raw)) return new ExigoConnectionError("Exigo rejected the username or password.", error);
  if (/ENOTFOUND|EAI_AGAIN|getaddrinfo/i.test(raw)) return new ExigoConnectionError(`Could not resolve the Exigo host. ${raw}`, error);
  if (/ECONNREFUSED/i.test(raw)) return new ExigoConnectionError("The Exigo host refused the connection. Check the port.", error);
  if (/self.signed|certificate/i.test(raw)) return new ExigoConnectionError(`TLS problem reaching Exigo: ${raw}`, error);
  return new ExigoConnectionError(`Exigo query failed: ${raw}`, error);
}
```

No retries in the hot path. A pool failure is not cached; the next call retries on its own.

## Schema probe (do this before writing queries)

```ts
export async function describeColumns(creds: ExigoCredentials, tables: string[]) {
  if (tables.length === 0) return [];
  // One bound parameter per table, not STRING_SPLIT: its collation can mismatch
  // INFORMATION_SCHEMA's on some tenants and fail outright.
  const placeholders = tables.map((_, i) => `@t${i}`).join(", ");
  return query<{ TABLE_NAME: string; COLUMN_NAME: string; DATA_TYPE: string }>(
    creds,
    `SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE
     FROM INFORMATION_SCHEMA.COLUMNS
     WHERE TABLE_SCHEMA = 'dbo' AND TABLE_NAME IN (${placeholders})
     ORDER BY TABLE_NAME, ORDINAL_POSITION`,
    (request, mssql) => {
      tables.forEach((table, i) => request.input(`t${i}`, mssql.NVarChar(128), table));
    },
  );
}
```

Expose it behind an admin route that returns names and types, never data. Invented column names (a per-line `CV` that does not exist) are how a deploy gets wasted.

## Representative query shapes

Tables and columns vary per tenant: confirm each against the probe before using it.

```ts
// Active standing orders (autoships). Use the status column, not a date.
const ACTIVE_AUTOORDERS_SQL = `
  SELECT DISTINCT ao.CustomerID AS customerId
  FROM dbo.AutoOrders ao
  WHERE ao.AutoOrderStatusID = 0
`;

// Subscription membership.
const ACTIVE_SUBSCRIPTION_SQL = `
  SELECT DISTINCT cs.CustomerID AS customerId
  FROM dbo.CustomerSubscriptions cs
  WHERE cs.SubscriptionID = @subscriptionId AND cs.IsActive = 1
`;

// One customer.
const CUSTOMER_SQL = `
  SELECT TOP 1 c.CustomerID AS customerId, c.CustomerTypeID AS customerTypeId
  FROM dbo.Customers c
  WHERE c.CustomerID = @customerId
`;

// Point balance.
const POINT_BALANCE_SQL = `
  SELECT cpa.PointBalance AS balance
  FROM dbo.CustomerPointAccounts cpa
  WHERE cpa.CustomerID = @customerId AND cpa.PointAccountID = @pointAccountId
`;
```

Bind with `request.input("subscriptionId", mssql.Int, id)`, `mssql.Decimal(12, 4)` for money-like thresholds, `mssql.NVarChar(n)` for strings.

### Validate ids before binding

```ts
export class ExigoIdentifierError extends Error {}

export function parseCustomerId(externalId: string): number {
  const id = Number(externalId);
  if (externalId.trim() === "" || !Number.isInteger(id)) {
    throw new ExigoIdentifierError(`Exigo customer ids are integers; got ${JSON.stringify(externalId)}`);
  }
  return id;
}
```

`Number("")` is 0 and `Number("ABC")` is NaN; either bound as Int matches nothing and would come back as a confident "no". Throw so the caller treats it as unreadable.

### Unreadable versus definitely false

A throw means "could not read, hold the current state". A returned `false` means "Exigo answered no". Callers that demote, revoke or charge on `false` must never receive it for a question that was not actually asked.

### Budgeting a shopper-facing callback

```ts
const result = await Promise.race([
  work,
  new Promise<"timeout">((resolve) => setTimeout(() => resolve("timeout"), budgetMs)),
]);
```

The race bounds the shopper's wait, not the Exigo work. Log a late completion, and attach a `.catch` to `work` so a late failure is not an unhandled rejection.
