---
name: Webhook & API health audit
description: Check registered webhooks against every resource/event Fluid can fire, flag missing coverage on critical events and configuration risk.
icon: radio-tower
---

# Goal

Audit `{{company.name}}`'s webhook configuration: which critical business events have no subscriber at all, which webhooks are inactive or duplicated, and where the biggest blind spot is.

# Steps

1. Call `fluid_api("/api/company/webhooks/resources", "GET")` to get the full catalog of resource/event pairs Fluid can fire (e.g. `order`: created/completed/shipped/cancelled/refunded/fulfillment_status_changed, `subscription`: started/billed/declined/cancelled/resumed, `customer`: created/updated/deleted).
2. Call `fluid_api("/api/company/webhooks?limit=100", "GET")`, paginating until exhausted. Keep `resource`, `event`, `url`, `active`, `http_method` per webhook.
3. Define a critical-events shortlist worth checking regardless of what the company happens to use today: `order.created`, `order.refunded`, `order.fulfillment_status_changed`, `subscription.declined`, `subscription.cancelled`, `customer.created`. For each, check whether an **active** webhook subscribes to it. Flag any gap.
4. Flag configuration risk in the registered set itself:
   - **Inactive** — `active: false` webhooks still configured (dead weight, or something someone meant to re-enable and forgot).
   - **Duplicate target** — two or more webhooks pointing at the same `url` for the same `resource`/`event` (double-delivery risk).
   - **Non-HTTPS or unusual method** — anything not using a standard POST to an `https://` URL.
5. Render three sections: **Critical-event gaps** (shortlist events with no active subscriber), **Configuration risk** (inactive/duplicate/non-standard), **Everything else registered** (brief summary count by resource).
6. End with a **Decision**: the single highest-priority gap to close first — almost always a missing `order.refunded` or `subscription.declined` subscriber if a downstream system (accounting, CRM, fulfillment) depends on being notified — and what registering it would unblock.
7. This is a read-only audit. Registering a new webhook is a write the user must confirm separately; don't call the create-webhook endpoint from this skill.
