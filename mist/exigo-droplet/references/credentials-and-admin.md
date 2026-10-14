# Credentials per installation, and the admin surface

Credentials live in the droplet's own DB, one row per installation, keyed by `companyId`. The SDK reads no env vars and stores nothing; the app supplies credentials.

## lib/schema.ts

```ts
export const exigoConnections = pgTable("exigo_connections", {
  companyId: text("company_id").primaryKey(),
  host: text("host"),
  database: text("database"),
  username: text("username"),
  // AES-256-GCM, keyed by CREDENTIAL_ENCRYPTION_KEY. Never returned to the browser.
  passwordCiphertext: text("password_ciphertext"),
  restBaseUrl: text("rest_base_url"),
  restUsername: text("rest_username"),
  restCompany: text("rest_company"),
  restPasswordCiphertext: text("rest_password_ciphertext"),
});
```

Add the matching idempotent `CREATE TABLE IF NOT EXISTS` / `ADD COLUMN IF NOT EXISTS` DDL to `lib/ensure-schema.ts` (PGlite locally, Neon in production).

## lib/secret-box.ts

```ts
import { createCipheriv, createDecipheriv, createHash, randomBytes } from "node:crypto";

const KEY_ENV = "CREDENTIAL_ENCRYPTION_KEY";

export class SecretBoxError extends Error {}

function key(): Buffer {
  const raw = process.env[KEY_ENV];
  if (!raw) throw new SecretBoxError(`${KEY_ENV} is not set.`);
  return createHash("sha256").update(raw).digest();
}

export function seal(plaintext: string): string {
  const iv = randomBytes(12);
  const cipher = createCipheriv("aes-256-gcm", key(), iv);
  const enc = Buffer.concat([cipher.update(plaintext, "utf8"), cipher.final()]);
  return ["v1", iv, cipher.getAuthTag(), enc]
    .map((part) => (typeof part === "string" ? part : part.toString("base64url")))
    .join(".");
}

export function open(sealed: string): string {
  const [version, iv, tag, data] = sealed.split(".");
  if (version !== "v1" || !iv || !tag || !data) {
    throw new SecretBoxError("Stored credential is not in the expected format.");
  }
  try {
    const decipher = createDecipheriv("aes-256-gcm", key(), Buffer.from(iv, "base64url"));
    decipher.setAuthTag(Buffer.from(tag, "base64url"));
    return Buffer.concat([
      decipher.update(Buffer.from(data, "base64url")),
      decipher.final(),
    ]).toString("utf8");
  } catch {
    throw new SecretBoxError("Stored credential could not be decrypted. Re-enter the password.");
  }
}
```

GCM is authenticated: a rotated key or tampered value fails to decrypt instead of yielding garbage. The user sets the key themselves with `fluid mist env set CREDENTIAL_ENCRYPTION_KEY=<value>`; never generate-and-print it, never edit Mist-managed `DATABASE_URL` or `FLUID_*` variables.

## Resolving credentials for a request

```ts
export async function resolveExigoCredentials(companyId: string, authToken: string | null) {
  const row = await db.query.exigoConnections.findFirst({
    where: eq(exigoConnections.companyId, companyId),
  });
  if (!row?.host || !row.database || !row.username || !row.passwordCiphertext) {
    throw new ExigoNotConfiguredError("Exigo is not configured for this installation.");
  }
  assertExigoHostAllowed(row.host);
  return {
    host: row.host,
    database: row.database,
    username: row.username,
    password: open(row.passwordCiphertext),
    egressProxy: resolveEgressProxy(authToken),
  };
}
```

No env-var fallback to shared Exigo credentials, ever. A missing row is an error response (for example 409 "not configured"), not a default.

## Admin settings route

- Authorise with `resolveFluidInstallation(request)`; scope every read and write to `context.companyId`.
- GET returns `{ host, database, username, passwordSet: boolean }`. Never the password or ciphertext.
- PUT: a blank password means keep the stored one; a non-blank password is `seal`ed. Validate the host with `assertExigoHostAllowed` before saving, so a bad value never lands in the DB for a later sweep or callback to dial.

## lib/admin/exigo-host.ts

The `dri` is a lookup key that travels in an iframe query string, so whoever holds one could otherwise store any hostname and have the server connect to it.

```ts
const ALLOWLIST_ENV = "EXIGO_HOST_ALLOWLIST"; // comma-separated hosts or *.suffix
const ALLOW_PRIVATE_ENV = "EXIGO_ALLOW_PRIVATE_HOSTS"; // "true" for local work only

export class ExigoHostError extends Error {}

export function isPrivateAddress(host: string): boolean {
  const lower = host.toLowerCase();
  if (lower === "localhost" || lower.endsWith(".localhost")) return true;
  if (lower === "::1" || lower === "[::1]" || /^\[?(fc|fd|fe80)/i.test(lower)) return true;
  if (!/^\d{1,3}(\.\d{1,3}){3}$/.test(lower)) return false;
  const [a, b] = lower.split(".").map(Number) as [number, number];
  if (Number.isNaN(a) || Number.isNaN(b) || a > 255 || b > 255) return true;
  return (
    a === 127 || a === 0 || a === 10 ||
    (a === 172 && b >= 16 && b <= 31) ||
    (a === 192 && b === 168) ||
    (a === 169 && b === 254) // link-local, includes the cloud metadata endpoint
  );
}

export function assertExigoHostAllowed(host: string): void {
  const trimmed = host.trim();
  if (!trimmed) throw new ExigoHostError("Exigo host cannot be empty");
  if (/[\s/\\@?#:]/.test(trimmed)) {
    throw new ExigoHostError("Exigo host must be a bare hostname: no scheme, path, port or credentials");
  }
  const allowlist = (process.env[ALLOWLIST_ENV] ?? "")
    .split(",").map((e) => e.trim().toLowerCase()).filter(Boolean);
  if (allowlist.length > 0) {
    const lower = trimmed.toLowerCase();
    const ok = allowlist.some((e) =>
      e.startsWith("*.") ? lower === e.slice(2) || lower.endsWith(e.slice(1)) : lower === e,
    );
    if (!ok) throw new ExigoHostError(`Exigo host ${trimmed} is not in ${ALLOWLIST_ENV}`);
    return;
  }
  if (process.env[ALLOW_PRIVATE_ENV] === "true") return;
  if (isPrivateAddress(trimmed)) {
    throw new ExigoHostError(`Exigo host ${trimmed} is a private, loopback or link-local address.`);
  }
}
```

This is not a complete SSRF defence (a public name whose DNS points inward still passes); the allowlist is the strong control. Port is a separate numeric field, default 1433, and through the proxy the destination port must also be on the proxy's allowlist.
