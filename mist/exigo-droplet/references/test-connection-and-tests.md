# Test-connection route and unit tests

## Test connection

A bare connect passes a wrong database, a user without rights on the table, or a subscription id that matches nothing. Run the real query and return counts, never rows.

```ts
// app/api/admin/exigo/test/route.ts
import { NextRequest, NextResponse } from "next/server";
import { FluidInstallationContextError, resolveFluidInstallation } from "@/lib/fluid/installation-context";
import { ensureSchema } from "@/lib/ensure-schema";

export const runtime = "nodejs";

const PROBE_BUDGET_MS = 15_000;

export async function POST(request: NextRequest) {
  let timer: ReturnType<typeof setTimeout> | undefined;
  try {
    await ensureSchema();
    const ctx = await resolveFluidInstallation(request);
    // verify session_token here once Fluid supplies it (see credentials-and-admin.md)
    const credentials = await resolveExigoCredentials(ctx.installation);

    const probe = (async () => {
      const autoOrders = await activeAutoOrderCustomerIds(credentials);
      return { activeAutoOrders: autoOrders.length };
    })();
    probe.catch(() => {}); // a late rejection after the budget wins must not be unhandled

    const counts = await Promise.race([
      probe,
      new Promise<never>((_, reject) => {
        timer = setTimeout(
          () => reject(new Error(`Exigo did not answer within ${PROBE_BUDGET_MS}ms`)),
          PROBE_BUDGET_MS,
        );
      }),
    ]);
    return NextResponse.json({ ok: true, ...counts });
  } catch (error) {
    if (error instanceof FluidInstallationContextError) {
      return NextResponse.json({ ok: false, error: "Installation not found" }, { status: 401 });
    }
    if (error instanceof ExigoNotConfiguredError) {
      return NextResponse.json({ ok: false, error: error.message }, { status: 409 });
    }
    if (error instanceof ExigoHostError) {
      return NextResponse.json({ ok: false, error: error.message }, { status: 422 });
    }
    const message = error instanceof Error ? error.message : String(error);
    console.error("[admin/exigo/test] probe failed:", message);
    return NextResponse.json({ ok: false, error: message }, { status: 200 });
  } finally {
    if (timer) clearTimeout(timer);
  }
}
```

- Only driver and connection failures answer 200 `{ ok: false, error }` with the translated message, so the admin UI can show it. An unresolved installation is 401 (the template's session-example also answers 401), not configured is 409, a refused host is 422.
- Reachable even while a feature kill switch is on: testing is how a merchant decides whether to enable anything. It writes nothing.
- Accept an optional single-customer probe (`?customerId=`), parsed and validated before any connection opens, to answer "why is this person not eligible?" with the same query the live path uses.
- For REST, hit a real endpoint and treat a 200 with a non-JSON body as failure; the API root serves HTML with 200 for any credentials. The SDK throws `ExigoApiError` for this.

## Unit tests (vitest)

Mock the SDK's `/sql` entry and assert the options handed to `getExigoPool`. A proxy that is configured but dropped on the floor fails as a connect timeout, the same symptom as having no proxy.

```ts
import { it, expect, vi, beforeEach } from "vitest";

const getExigoPool = vi.fn();
vi.mock("@fluid-app/exigo-connection-sdk/sql", () => ({
  getExigoPool: (...args: unknown[]) => getExigoPool(...args),
}));

const { withPool } = await import("./client");
// The real class from the package root, so the instanceof branch under test matches.
import { ExigoProxyError } from "@fluid-app/exigo-connection-sdk";

const CREDS = { host: "tenant.example.net", database: "Reporting", username: "reader", password: "x" };
const PROXY = { url: "https://egress.example.com", token: "dit_test" };

beforeEach(() => {
  getExigoPool.mockReset();
  getExigoPool.mockResolvedValue({});
});

it("passes egressProxy through when present", async () => {
  await withPool({ ...CREDS, egressProxy: PROXY }, async () => 1);
  expect(getExigoPool.mock.calls[0][1]).toMatchObject({ egressProxy: PROXY });
});

it("omits the key entirely when there is no proxy", async () => {
  await withPool(CREDS, async () => 1);
  expect(getExigoPool.mock.calls[0][1]).not.toHaveProperty("egressProxy");
});

it("keeps the timeouts", async () => {
  await withPool({ ...CREDS, egressProxy: PROXY }, async () => 1);
  expect(getExigoPool.mock.calls[0][1]).toMatchObject({
    connectTimeoutMs: 12_000,
    requestTimeoutMs: 25_000,
  });
});

it("reports a proxy refusal as the proxy's problem", async () => {
  getExigoPool.mockRejectedValue(
    new ExigoProxyError("refused", "sql", { status: 403 }),
  );
  await expect(withPool(CREDS, async () => 1)).rejects.toThrow(/allowlist/);
});
```

Also test `resolveEgressProxy` directly: unset URL returns `undefined`; URL set with a blank or missing token throws; URL plus token returns `{ url, token }`. Set and restore `process.env.FLUID_EGRESS_PROXY_URL` with `vi.stubEnv` / `vi.unstubAllEnvs()`; assigning `undefined` to `process.env.X` stores the string `"undefined"`.

Cover each `ExigoProxyError` status (407, 403, 502, 504, 503) with its own assertion: each has a different owner, so a message that falls through to the generic branch sends the merchant to the wrong place.
