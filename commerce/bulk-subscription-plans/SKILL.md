---
name: Bulk Subscription Plans
description: Bulk create subscription plans and apply them to all products or a selected subset — in one shot.
icon: refresh-cw
category: Commerce
---

# Bulk Subscription Plans

Create one or more subscription plans for **{{company.name}}** and apply them to products in bulk. Saves you from creating plans one by one in the admin and linking each product manually.

Today is {{today}}.

## 0. Ask first

Before running anything, ask the user these questions in one message:

> **1. What plans do you want to create?**
> Describe each plan in plain English — e.g. "Monthly at 10% off, Quarterly at 15% off, Annual at 20% off." You can also request common presets:
> - **Starter** — Monthly + Annual with 10% and 18% off
> - **Standard** — Monthly / Quarterly / Annual at 10% / 15% / 20% off
> - **Consumables** — Monthly / Every 2 months / Every 3 months at 10% / 12% / 15% off (good for replenishables)
>
> **2. Which products should these plans apply to?**
> - **All products** — apply to every active product
> - **Select products** — I'll fetch your catalog and let you pick
> - **All except…** — apply to everything except products you name

Wait for their answers. Do not proceed until you have both.

## 1. Pre-flight check

Verify the company has products:

```bash
FLUID_TOKEN=$(fluid-token)
curl -s "https://api.fluid.app/api/v2/integrations/products?per_page=5" \
  -H "Authorization: Bearer $FLUID_TOKEN" | python3 -c "
import json, sys
d = json.load(sys.stdin)
prods = d.get('products', [])
active = [p for p in prods if any(v.get('status') == 'active' for v in p.get('variants', []))]
print(f'Total products: {len(prods)}, active: {len(active)}')
if not active:
    print('ERROR: No active products found.')
"
```

If no active products exist, stop and tell the user to import products first.

## 2. Fetch full product list (if needed)

If the user chose "Select products" or "All except…", fetch the full catalog and display a numbered list:

```bash
FLUID_TOKEN=$(fluid-token)
python3 - << 'PYEOF'
import json, os, subprocess

token = subprocess.check_output("fluid-token", shell=True).decode().strip()
headers = {"Authorization": f"Bearer {token}"}

import urllib.request
page, products = 1, []
while True:
    url = f"https://api.fluid.app/api/v2/integrations/products?per_page=100&page={page}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as r:
        data = json.load(r)
    batch = data.get("products", [])
    if not batch:
        break
    products.extend(batch)
    if len(batch) < 100:
        break
    page += 1

print(f"\nFound {len(products)} products:\n")
for i, p in enumerate(products, 1):
    name = p.get("name", "Unnamed")
    pid = p.get("id")
    active = any(v.get("status") == "active" for v in p.get("variants", []))
    status = "active" if active else "inactive"
    print(f"  {i:3}. [{pid}] {name} ({status})")
PYEOF
```

Ask the user to specify which products by number or name. Then map their selection to product IDs before continuing.

## 3. Build the plan definitions

Based on the user's answers, construct a list of plan configs. Use this reference:

| Preset name | Plans |
|-------------|-------|
| Starter | Monthly 10% off, Annual 18% off |
| Standard | Monthly 10%, Quarterly 15%, Annual 20% off |
| Consumables | Monthly 10%, Every-2-months 12%, Quarterly 15% off |

For custom plans, parse the user's description. Map frequencies to `billing_interval` + `billing_interval_unit`:

| User says | billing_interval | billing_interval_unit |
|-----------|-----------------|----------------------|
| Weekly | 1 | week |
| Monthly | 1 | month |
| Every 2 months | 2 | month |
| Quarterly | 3 | month |
| Every 6 months | 6 | month |
| Annual / Yearly | 1 | year |

`shipping_interval` and `volume_interval` should match `billing_interval`/`billing_interval_unit` unless the user specifies otherwise.

Discount type: use `percentage` for "% off" and `fixed_amount` for "$X off". `price_adjustment_amount` is a positive number (e.g. 10 for 10% off).

## 4. Create the plans

Run this script, substituting `PLANS_JSON` with the array of plan configs you built in step 3:

```bash
FLUID_TOKEN=$(fluid-token)
python3 - << 'PYEOF'
import json, os, subprocess, urllib.request, urllib.error

token = subprocess.check_output("fluid-token", shell=True).decode().strip()
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
}

# Substitute the list of plans before running
plans = PLANS_JSON_PLACEHOLDER

created = []
failed = []

for plan in plans:
    body = json.dumps({"subscription_plan": plan}).encode()
    req = urllib.request.Request(
        "https://api.fluid.app/api/subscription_plans",
        data=body,
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as r:
            result = json.load(r)
        sp = result.get("subscription_plan", {})
        created.append({"id": sp["id"], "name": sp["name"]})
        print(f"  Created: {sp['name']} (id={sp['id']})")
    except urllib.error.HTTPError as e:
        err = e.read().decode()
        failed.append({"plan": plan["name"], "error": err})
        print(f"  FAILED: {plan['name']} — {err}")

print(f"\nDone. Created: {len(created)}, Failed: {len(failed)}")
if failed:
    print("Failures:", json.dumps(failed, indent=2))

# Save created plan IDs for next step
with open("/tmp/fluid_created_plans.json", "w") as f:
    json.dump(created, f)
PYEOF
```

If any plans fail, diagnose the error and fix before proceeding.

## 5. Apply plans to products

Now associate each created plan with the target products. Each plan-to-product association requires a separate API call.

```bash
FLUID_TOKEN=$(fluid-token)
python3 - << 'PYEOF'
import json, os, subprocess, urllib.request, urllib.error, time

token = subprocess.check_output("fluid-token", shell=True).decode().strip()
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
}

# Load created plans from step 4
with open("/tmp/fluid_created_plans.json") as f:
    plans = json.load(f)

# Substitute product IDs — list of integers
product_ids = PRODUCT_IDS_PLACEHOLDER

success, failed = 0, []

for plan in plans:
    plan_id = plan["id"]
    plan_name = plan["name"]
    for product_id in product_ids:
        body = json.dumps({
            "subscription_plan": {"id": plan_id},
            "product_subscription_plans": {
                "product_id": product_id,
                "default": False,
            }
        }).encode()
        req = urllib.request.Request(
            f"https://api.fluid.app/api/subscription_plans/{plan_id}",
            data=body,
            headers=headers,
            method="PATCH",
        )
        try:
            with urllib.request.urlopen(req) as r:
                r.read()
            success += 1
        except urllib.error.HTTPError as e:
            err = e.read().decode()
            failed.append({"plan": plan_name, "product_id": product_id, "error": err})
        time.sleep(0.05)  # avoid rate limiting

print(f"\nAssociations complete: {success} succeeded, {len(failed)} failed")
if failed:
    print("Failures:")
    for f in failed:
        print(f"  Plan '{f['plan']}' + product {f['product_id']}: {f['error']}")
PYEOF
```

## 6. Report results

Print a clean summary:

```
Subscription Plans Created for {{company.name}}
────────────────────────────────────────────────
Plan Name            Frequency    Discount    Products Applied
─────────────────────────────────────────────────────────────
Monthly 10% Off      Monthly      10% off     42
Quarterly 15% Off    Quarterly    15% off     42
Annual 20% Off       Annual       20% off     42

Total plans created: 3
Total product associations: 126
```

If any associations failed, list the affected plan + product IDs and suggest the user verify those products exist and are accessible.

Finally, remind the user:
> Plans are created but customers won't see them until subscription purchasing is enabled on your storefront. To activate it, go to **Commerce → Subscriptions → Settings** in your Fluid admin.
