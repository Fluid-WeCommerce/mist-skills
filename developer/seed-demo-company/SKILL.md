---
name: Seed Demo Company
description: Populate the active Fluid company with realistic demo data - customers, orders with products, active subscriptions, and mixed sources - using the company's existing product catalog.
icon: database
category: developer
---

# Seed Demo Company

Seed **{{company.name}}** with realistic demo data using its existing product catalog. Generates customers, orders (with real product links), and active subscriptions with varied frequencies and payment methods.

Today is {{today}}.

## 0. Ask first

Before running anything, ask the user exactly one question:

> **How many total orders would you like to seed?**
> A good starting point is 300. Subscriptions will account for roughly 25% of that total and will all be active.

Wait for their answer. Do not proceed until you have a number.

## 1. Pre-flight check

Run the following to confirm the company has usable products:

```bash
FLUID_TOKEN=$(fluid-token) python3 - << 'PYEOF'
import json
import os
import subprocess
import sys

token = os.environ["FLUID_TOKEN"]
products = []
page = 1

while True:
    result = subprocess.run(
        [
            "curl",
            "-sS",
            "--fail-with-body",
            "https://api.fluid.app/api/v2/integrations/products"
            f"?per_page=100&page={page}",
            "-H",
            f"Authorization: Bearer {token}",
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(result.stderr or result.stdout, file=sys.stderr)
        sys.exit(result.returncode)

    data = json.loads(result.stdout)
    batch = data.get("products", [])
    products.extend(batch)
    if not batch or page >= data.get("meta", {}).get("total_pages", 1):
        break
    page += 1

usable_variants = []
for product in products:
    for variant in product.get("variants", []):
        if variant.get("status") != "active" or not variant.get("sku"):
            continue
        for country in variant.get("variant_countries", []):
            try:
                price = float(country.get("price") or 0)
            except (TypeError, ValueError):
                price = 0
            if country.get("currency_code") == "USD" and price > 0:
                usable_variants.append(variant)
                break

print(f"Products found: {len(products)}, usable USD variants: {len(usable_variants)}")
if not usable_variants:
    print("ERROR: No active, SKU-backed, USD-priced variants found.")
    sys.exit(1)
PYEOF
```

If no usable variants are found, stop and tell the user they need to set up products first.

## 2. Run the seed script

Replace `ORDER_COUNT` with the number the user gave you, then run this script. It will take several minutes for large counts - print progress as it runs.

```bash
FLUID_TOKEN=$(fluid-token) python3 - << 'PYEOF'
import json, os, subprocess, random, time, sys
from datetime import datetime, timedelta

# ── Config ────────────────────────────────────────────────────────────────────
ORDER_COUNT    = ORDER_COUNT_PLACEHOLDER   # replaced before execution
SUB_FRACTION   = 0.25                      # ~25% of orders come from subscriptions
SOURCE_WEIGHTS = {"web": 55, "mobile": 35, "backoffice": 10}
PROMO_RATE     = 0.12                      # 12% of non-sub orders get a promo code
PROMO_CODES    = ["WELCOME20", "SAVE15", "FREESHIP", "FLASH25", "VIP10"]
STATUS_WEIGHTS = [("paid",7), ("paid",7), ("paid",7), ("paid",7), ("pending",2), ("refunded",1)]
BATCH_SIZE     = 10
random.seed(42)

TOKEN    = os.environ["FLUID_TOKEN"]
BASE_URL = "https://api.fluid.app"
HEADERS  = ["-H", f"Authorization: Bearer {TOKEN}", "-H", "Content-Type: application/json"]

# ── Helpers ───────────────────────────────────────────────────────────────────
def api_get(path):
    r = subprocess.run(["curl", "-s"] + HEADERS[:2] + [f"{BASE_URL}{path}"],
                       capture_output=True, text=True)
    return json.loads(r.stdout) if r.stdout.strip() else {}

def api_post(path, payload, retries=2):
    for attempt in range(retries + 1):
        r = subprocess.run(["curl", "-s", "-X", "POST"] + HEADERS +
                           ["-d", json.dumps(payload), f"{BASE_URL}{path}"],
                           capture_output=True, text=True)
        if r.stdout.strip():
            return json.loads(r.stdout)
        if attempt < retries:
            time.sleep(0.5)
    return {}

def random_date(days_ago_min=1, days_ago_max=90):
    """Weighted toward recent dates with natural weekly rhythm."""
    # Build daily order weights over the window
    total_days = days_ago_max - days_ago_min
    day_weights = []
    for i in range(total_days):
        days_ago = days_ago_max - i
        dt = datetime.now() - timedelta(days=days_ago)
        weekday_factor = 1.3 if dt.weekday() < 5 else 0.6  # weekdays busier
        recency_factor = 0.5 + (i / total_days) * 1.0      # more recent = more likely
        day_weights.append(weekday_factor * recency_factor)
    chosen = random.choices(range(total_days), weights=day_weights)[0]
    days_ago = days_ago_max - chosen
    dt = datetime.now() - timedelta(days=days_ago, hours=random.randint(0, 23), minutes=random.randint(0, 59))
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

def pick_source():
    pool = []
    for src, w in SOURCE_WEIGHTS.items():
        pool.extend([src] * w)
    return random.choice(pool)

def pick_status():
    pool = [s for s, w in STATUS_WEIGHTS for _ in range(w)]
    return random.choice(pool)

print("=" * 60)
print(f"Seeding {ORDER_COUNT} orders for this company...")
print("=" * 60)

# ── Phase 1: Discover company context ────────────────────────────────────────
print("\n[1/5] Discovering company context...")

# Get subscription plans
plans_resp = api_get("/api/subscription_plans")
plans = [p for p in plans_resp.get("subscription_plans", []) if p.get("active")]
if not plans:
    print("  WARNING: No active subscription plans found. Subscriptions will be skipped.")
PLAN_WEIGHTS_LIST = []
for p in plans:
    interval = p.get("billing_interval", 1)
    unit = p.get("billing_interval_unit", "month")
    # Weight: monthly most common, longer intervals less so
    if unit == "month" and interval == 1:
        weight = 40
    elif unit == "month" and interval == 2:
        weight = 20
    elif unit == "month" and interval == 3:
        weight = 15
    elif unit == "week" and interval == 1:
        weight = 12
    elif unit == "week" and interval == 2:
        weight = 10
    else:
        weight = 5
    PLAN_WEIGHTS_LIST.extend([p["id"]] * weight)
print(f"  Subscription plans: {len(plans)}")

# Find payment account for test cards (Bogus/dummy gateway preferred)
# Searches all accounts (active or not) and activates the Bogus one if found
# Must fetch per_page=200 — endpoint defaults to 10 and gateway may be on later pages
accounts_resp = api_get("/api/payment_accounts?per_page=200")
accounts = accounts_resp.get("payment_accounts", [])
if not accounts:
    print(f"  WARNING: /api/payment_accounts returned no accounts (raw: {accounts_resp})")
gateway = None
for a in accounts:
    name    = (a.get("name") or "").lower()
    adapter = (a.get("adapter_class") or "").lower()
    display = (a.get("display_name") or "").lower()
    if "bogus" in adapter or "bogus" in name or "dummy" in name or "dummy" in display:
        gateway = a
        break
if not gateway:
    active_accounts = [a for a in accounts if a.get("active")]
    gateway = active_accounts[0] if active_accounts else None
# Ensure it's active
if gateway and not gateway.get("active"):
    act_r = subprocess.run(
        ["curl", "-s", "-X", "PATCH"] + HEADERS +
        ["-d", json.dumps({"payment_account": {"active": True}}),
         f"{BASE_URL}/api/payment_accounts/{gateway['id']}"],
        capture_output=True, text=True,
    )
    act_resp = json.loads(act_r.stdout) if act_r.stdout.strip() else {}
    if act_resp.get("payment_account", {}).get("active"):
        gateway["active"] = True
        print(f"  Activated gateway: {gateway['name']}")
    else:
        print(f"  WARNING: Failed to activate gateway {gateway['name']}: {act_resp}")
        gateway = None
gateway_id = gateway["id"] if gateway else None
print(f"  Payment gateway: {gateway['name'] if gateway else 'none found'} (id={gateway_id})")

# Get fluid_shop from ~/.fluid/config.json (set by `fluid switch`)
fluid_shop = ""
try:
    import pathlib
    config_path = pathlib.Path.home() / ".fluid" / "config.json"
    config = json.loads(config_path.read_text())
    active_profile = config.get("activeProfile", "")
    fluid_shop = config.get("profiles", {}).get(active_profile, {}).get("fluidShop", "")
except Exception:
    pass
print(f"  Company shop: {fluid_shop or '(unknown - subscriptions will be skipped)'}")

# ── Phase 2: Collect active products ─────────────────────────────────────────
print("\n[2/5] Loading active products...")

all_products = []
page = 1
while True:
    d = api_get(f"/api/v2/integrations/products?per_page=100&page={page}")
    batch = d.get("products", [])
    if not batch:
        break
    all_products.extend(batch)
    if page >= d.get("meta", {}).get("total_pages", 1):
        break
    page += 1

# Build a flat list of usable variants per currency
# Each entry: {variant_id, sku, title, price, currency, country_iso_3}
variants_by_currency = {}
for p in all_products:
    p_title = p.get("title") or ""
    for v in p.get("variants", []):
        if v.get("status") != "active":
            continue
        v_sku = v.get("sku") or ""
        v_title = v.get("title") or p_title
        if not v_sku:
            continue  # product_sku must be non-null for order item linking to work
        seen_currencies = set()
        for vc in v.get("variant_countries", []):
            currency = vc.get("currency_code", "")
            price = float(vc.get("price") or 0)
            if not currency or price <= 0 or currency in seen_currencies:
                continue
            seen_currencies.add(currency)
            if currency not in variants_by_currency:
                variants_by_currency[currency] = []
            entry = {
                "variant_id": v["id"],
                "sku": v_sku,
                "title": v_title,
                "price": price,
                "currency": currency,
            }
            if entry not in variants_by_currency[currency]:
                variants_by_currency[currency].append(entry)

usd_variants = variants_by_currency.get("USD", [])
if not usd_variants:
    print("  ERROR: No active USD-priced variants found. Cannot seed.")
    sys.exit(1)

print(f"  Active products: {len(all_products)}, USD variants: {len(usd_variants)}")
print(f"  Currencies available: {sorted(variants_by_currency.keys())}")

# ── Phase 3: Seed customers ───────────────────────────────────────────────────
print("\n[3/5] Seeding customers...")

N_CUSTOMERS = max(30, min(ORDER_COUNT // 2, 150))

# Pre-built name/location pool (enough for up to 150 unique customers)
FIRST_NAMES = [
    "Jake","Aisha","Derek","Maria","Tyler","Priya","Noah","Emma","Caleb","Sofia",
    "Marcus","Lily","Ethan","Zoe","Liam","Ava","Owen","Mia","Ryan","Nora",
    "Finn","Isla","Gabe","Luna","Cole","Hazel","Beau","Ivy","Rex","Vera",
    "Miles","Dani","Leo","Wren","Chase","Piper","Sage","Brooks","Cleo","Drew",
    "Skye","Tate","Rue","Jace","Nell","Gray","Ada","Zane","Blair","Penn",
    "Alex","Jordan","Morgan","Casey","Quinn","Avery","Riley","Taylor","Cameron","Logan",
    "Hayden","Reese","Peyton","Dakota","Rowan","Emery","Finley","Skylar","Kendall","Parker",
    "Sydney","Bailey","Corey","Jamie","Robin","Terry","Jesse","Pat","Dana","Blake",
    "Sam","Charlie","Andy","Chris","Leslie","Francis","Tracy","Kerry","Lee","Dale",
    "Kim","Jan","Lynn","Robin","Shannon","Shawn","Dennis","Jamie","Terri","Remy",
    "Ash","Phoenix","River","Sage","Kai","Remy","Nico","Sable","Frost","Dex",
    "Tatum","Emory","Lennox","Harlow","Beckett","Sloane","Marlowe","Rafferty","Saoirse","Blythe",
    "Cormac","Imogen","Stellan","Waverly","Theron","Indigo","Cassian","Soleil","Zephyr","Lyra",
    "Orion","Celeste","Atticus","Seren","Caspian","Aurelia","Thane","Veda","Caius","Isolde",
]
LAST_NAMES = [
    "Morrison","Okafor","Chen","Santos","Walsh","Sharma","Rivera","Thompson","Jordan","Nguyen",
    "Davis","Park","Brown","Garcia","Wilson","Martinez","Taylor","Anderson","Jackson","White",
    "Harris","Lewis","Clark","Robinson","Walker","Hall","Allen","Young","King","Scott",
    "Green","Baker","Perez","Mitchell","Carter","Roberts","Turner","Phillips","Campbell","Parker",
    "Evans","Edwards","Collins","Stewart","Sanchez","Morris","Rogers","Reed","Cook","Morgan",
    "Bell","Murphy","Bailey","Rivera","Cooper","Richardson","Cox","Howard","Ward","Torres",
    "Peterson","Gray","Ramirez","James","Watson","Brooks","Kelly","Sanders","Price","Bennett",
    "Wood","Barnes","Ross","Henderson","Coleman","Jenkins","Perry","Powell","Long","Patterson",
    "Hughes","Flores","Washington","Butler","Simmons","Foster","Gonzales","Bryant","Alexander","Russell",
    "Griffin","Diaz","Hayes","Myers","Ford","Hamilton","Graham","Sullivan","Wallace","Woods",
    "West","Cole","Jordan","Owens","Reynolds","Fisher","Ellis","Harrison","Gibson","Mcdonald",
    "Cruz","Marshall","Ortiz","Gomez","Murray","Freeman","Wells","Webb","Simpson","Stevens",
    "Tucker","Porter","Hunter","Hicks","Crawford","Henry","Boyd","Mason","Morales","Kennedy",
    "Warren","Dixon","Ramos","Reyes","Burns","Gordon","Shaw","Holmes","Rice","Robertson",
]
US_LOCATIONS = [
    ("847 Pine St","Chicago","IL","60601"),("233 Oak Ave","Atlanta","GA","30301"),
    ("1420 Elm Blvd","Seattle","WA","98101"),("56 Maple Dr","Phoenix","AZ","85001"),
    ("99 Cedar Ln","Denver","CO","80201"),("3310 Birch Rd","Austin","TX","78701"),
    ("15 Walnut St","Miami","FL","33101"),("720 Spruce Ave","Nashville","TN","37201"),
    ("488 Willow Way","Portland","OR","97201"),("2201 Ash St","San Diego","CA","92101"),
    ("671 Poplar Ave","Columbus","OH","43201"),("330 Hickory Ct","Minneapolis","MN","55401"),
    ("88 Magnolia Dr","Charlotte","NC","28201"),("1700 Peach Blvd","Dallas","TX","75201"),
    ("543 Dogwood Ln","San Antonio","TX","78201"),("210 Sycamore St","Las Vegas","NV","89101"),
    ("1890 Juniper Rd","Salt Lake City","UT","84101"),("76 Redwood Ave","Sacramento","CA","94201"),
    ("930 Aspen Way","Kansas City","MO","64101"),("2345 Cottonwood Rd","Raleigh","NC","27601"),
    ("180 Ponderosa Pl","Richmond","VA","23219"),("55 Sequoia Dr","Louisville","KY","40201"),
    ("422 Cypress Ave","Indianapolis","IN","46201"),("1011 Fir St","Jacksonville","FL","32201"),
    ("888 Larch Blvd","Memphis","TN","38101"),("344 Palm Dr","Baltimore","MD","21201"),
    ("677 Olive St","Oklahoma City","OK","73101"),("215 Chestnut Ave","Milwaukee","WI","53201"),
    ("500 Acacia Way","Tucson","AZ","85701"),("129 Banyan Rd","Fresno","CA","93701"),
    ("803 Elm Pl","Albuquerque","NM","87101"),("1560 Oak Ridge Dr","Omaha","NE","68101"),
    ("990 Cactus Blvd","El Paso","TX","79901"),("47 Fern Lane","Boise","ID","83701"),
    ("302 Ivy St","Spokane","WA","99201"),("1222 Laurel Ave","Richmond","VA","23219"),
    ("58 Orchid Ct","Anchorage","AK","99501"),("711 Gardenia Dr","Tampa","FL","33601"),
    ("2030 Rosemary Rd","Boston","MA","02101"),("444 Lavender Ln","Providence","RI","02901"),
    ("183 Jasmine Blvd","Hartford","CT","06101"),("629 Violet Way","Newark","NJ","07101"),
    ("1875 Daisy St","Buffalo","NY","14201"),("555 Tulip Ave","Pittsburgh","PA","15201"),
    ("2100 Azalea Ln","Cincinnati","OH","45201"),("76 Begonia Ct","Detroit","MI","48201"),
    ("440 Camellia Blvd","St. Louis","MO","63101"),("308 Peony Dr","New Orleans","LA","70101"),
    ("99 Marigold Pl","Birmingham","AL","35201"),("765 Dahlia Way","Knoxville","TN","37901"),
]
# International locations (only if non-USD variants exist)
INTL_LOCATIONS = {
    "DE": [("12 Hauptstraße","Berlin","DE","10115","EUR"),("45 Bahnhofstr","Munich","DE","80333","EUR")],
    "FR": [("8 Rue de Rivoli","Paris","FR","75001","EUR"),("22 Cours Mirabeau","Marseille","FR","13100","EUR")],
    "CA": [("100 Queen St W","Toronto","ON","M5H2N2","CAD"),("789 Robson St","Vancouver","BC","V6Z1J7","CAD")],
    "MX": [("Av. Reforma 123","Mexico City","CDMX","06600","MXN"),("Blvd. Kukulcan 5","Cancún","QR","77500","MXN")],
    "JP": [("1-1 Shinjuku","Tokyo","Tokyo","160-0022","JPY"),("2-3 Namba","Osaka","Osaka","542-0076","JPY")],
    "GB": [("10 Oxford St","London","England","W1D1BS","GBP"),("5 Buchanan St","Glasgow","Scotland","G12SD","GBP")],
    "AU": [("100 George St","Sydney","NSW","2000","AUD"),("250 Bourke St","Melbourne","VIC","3000","AUD")],
    "BR": [("Av. Paulista 1000","São Paulo","SP","01310-100","BRL"),("Rua Copacabana 200","Rio de Janeiro","RJ","22020-001","BRL")],
}

# Determine how many intl customers to create
has_intl = any(c != "USD" for c in variants_by_currency)
intl_fraction = 0.20 if has_intl else 0.0
n_us   = int(N_CUSTOMERS * (1 - intl_fraction))
n_intl = N_CUSTOMERS - n_us

# Build customer list
customers_to_create = []
used_names = set()
rand_state = random.Random(42)

for i in range(N_CUSTOMERS):
    is_intl = (i >= n_us) and n_intl > 0
    ext_id  = f"DEMO-CUST-{i+1:04d}"

    first = rand_state.choice(FIRST_NAMES)
    last  = rand_state.choice(LAST_NAMES)
    while (first, last) in used_names:
        first = rand_state.choice(FIRST_NAMES)
        last  = rand_state.choice(LAST_NAMES)
    used_names.add((first, last))

    email_num   = i + 1
    email_local = f"{first.lower()}.{last.lower()}{email_num if email_num > 1 else ''}"
    domain      = rand_state.choice(["gmail.com","icloud.com","yahoo.com","outlook.com"])
    email       = f"{email_local}@{domain}"

    if not is_intl:
        addr1, city, state, postal = rand_state.choice(US_LOCATIONS)
        country_code = "US"
        currency     = "USD"
        address_attrs = {
            "name": f"{first} {last}",
            "address1": addr1,
            "city": city,
            "state": state,
            "postal_code": postal,
            "country_code": "US",
            "default": True,
        }
    else:
        intl_currencies = [c for c in variants_by_currency if c != "USD" and c in
                           {"EUR","CAD","MXN","JPY","BRL","GBP","AUD"}]
        if not intl_currencies:
            # Fall back to US
            addr1, city, state, postal = rand_state.choice(US_LOCATIONS)
            country_code = "US"
            currency     = "USD"
            address_attrs = {
                "name": f"{first} {last}",
                "address1": addr1,
                "city": city,
                "state": state,
                "postal_code": postal,
                "country_code": "US",
                "default": True,
            }
        else:
            currency_code = rand_state.choice(intl_currencies)
            currency      = currency_code
            # Map currency to country
            currency_country_map = {
                "EUR": rand_state.choice(["DE","FR"]),
                "CAD": "CA",
                "MXN": "MX",
                "JPY": "JP",
                "BRL": "BR",
                "GBP": "GB",
                "AUD": "AU",
            }
            country_code_2 = currency_country_map.get(currency_code, "US")
            locs = INTL_LOCATIONS.get(country_code_2, US_LOCATIONS[:2])
            if locs and len(locs[0]) == 5:
                addr1, city, state, postal, _ = rand_state.choice(locs)
                address_attrs = {
                    "name": f"{first} {last}",
                    "address1": addr1,
                    "city": city,
                    "state": state,
                    "postal_code": postal,
                    "country_code": country_code_2,
                    "default": True,
                }
            else:
                addr1, city, state, postal = rand_state.choice(US_LOCATIONS)
                country_code_2 = "US"
                currency = "USD"
                address_attrs = {
                    "name": f"{first} {last}",
                    "address1": addr1,
                    "city": city,
                    "state": state,
                    "postal_code": postal,
                    "country_code": "US",
                    "default": True,
                }
            country_code = country_code_2

    customers_to_create.append({
        "ext_id": ext_id,
        "first": first,
        "last": last,
        "email": email,
        "address_attrs": address_attrs,
        "country_code": country_code,
        "currency": currency,
    })

# Batch-create customers
customer_payload = []
for c in customers_to_create:
    customer_payload.append({
        "email": c["email"],
        "first_name": c["first"],
        "last_name": c["last"],
        "external_integration_market_id": c["ext_id"],
        "default_address_attributes": c["address_attrs"],
    })

customers_created = 0
for i in range(0, len(customer_payload), BATCH_SIZE):
    batch = customer_payload[i:i+BATCH_SIZE]
    resp  = api_post("/api/v2/integrations/customers", {"customers": batch})
    customers_created += len(resp.get("customers", []))
    time.sleep(0.1)

print(f"  Created {customers_created}/{N_CUSTOMERS} customers ({n_us} US, {n_intl} intl)")

# ── Phase 4: Add payment methods (US customers only, for subscriptions) ───────
print("\n[4/5] Adding test payment methods for subscription customers...")

TEST_CARDS = [
    {"number": "4111111111111111", "exp_month": 12, "exp_year": 2028},
    {"number": "4242424242424242", "exp_month": 11, "exp_year": 2027},
    {"number": "5500005555555559", "exp_month": 10, "exp_year": 2029},
    {"number": "4000056655665556", "exp_month":  9, "exp_year": 2028},
    {"number": "4916338506082832", "exp_month":  8, "exp_year": 2027},
    {"number": "4539578763621486", "exp_month":  7, "exp_year": 2028},
]

# Fetch customer IDs from the orders endpoint (most reliable)
all_cust_ids = set()
pg = 1
while len(all_cust_ids) < 500:
    d = api_get(f"/api/v2/orders?per_page=100&page={pg}")
    batch = d.get("orders", [])
    if not batch:
        break
    for o in batch:
        if o.get("customer_id"):
            all_cust_ids.add(o["customer_id"])
    if pg >= d.get("meta", {}).get("total_pages", 1):
        break
    pg += 1

# Also get fresh customer IDs from the customers we just created
fresh_customers_resp = api_get(f"/api/v2/integrations/customers?per_page=200")
fresh_customers = fresh_customers_resp.get("customers", [])
demo_customers = [c for c in fresh_customers
                  if (c.get("external_integration_market_id") or "").startswith("DEMO-CUST-")]

pm_data = {}  # customer_id -> {address_id, pm_id, currency}
pm_added = 0

for c in demo_customers:
    cid = c["id"]
    # Get address
    cust_detail = api_get(f"/api/customers/{cid}")
    cust = cust_detail.get("customer", cust_detail)
    addresses = cust.get("addresses", [])
    if not addresses:
        continue
    addr_id = addresses[0]["id"]
    country  = addresses[0].get("country_code", "US")
    currency = "USD" if country == "US" else None
    if not currency:
        for c2 in customers_to_create:
            if c2["ext_id"] == cust.get("external_integration_market_id"):
                currency = c2["currency"]
                break
        if not currency:
            currency = "USD"

    # Only add payment method if USD (Bogus gateway handles USD)
    pm_id = None
    if currency == "USD" and gateway_id:
        card = TEST_CARDS[cid % len(TEST_CARDS)]
        pm_resp = api_post(f"/api/customers/{cid}/payment_methods", {
            "type": "credit_card",
            "country_code": "US",
            "payment_method": {
                "token": card["number"],
                "exp_month": card["exp_month"],
                "exp_year": card["exp_year"],
            },
            "default_payment_method": True,
        })
        pm_id = pm_resp.get("payment_method", {}).get("id")
        if pm_id:
            pm_added += 1
        elif pm_added == 0 and len(pm_data) == 0:
            print(f"  PM error for first customer: {pm_resp}")

    pm_data[cid] = {"address_id": addr_id, "pm_id": pm_id, "currency": currency, "country": country}
    time.sleep(0.05)

print(f"  Payment methods added: {pm_added}")

# ── Phase 5: Create subscriptions (and their first orders) ───────────────────
N_SUBS = int(ORDER_COUNT * SUB_FRACTION) if plans else 0
sub_orders_created = 0

if N_SUBS > 0 and fluid_shop:
    print(f"\n[5a/5] Creating {N_SUBS} subscriptions (each generates 1 order)...")

    eligible_for_subs = [(cid, data) for cid, data in pm_data.items()
                         if data["currency"] == "USD" and data["pm_id"]]

    if not eligible_for_subs:
        print("  WARNING: No USD customers with payment methods. Skipping subscriptions.")
        N_SUBS = 0
    else:
        cust_sub_count = {cid: 0 for cid, _ in eligible_for_subs}
        sub_errors = 0

        for sub_i in range(N_SUBS):
            # Pick customer with fewest subscriptions
            cid, cdata = sorted(eligible_for_subs, key=lambda x: cust_sub_count[x[0]])[sub_i % len(eligible_for_subs)]

            variant_info = random.choice(usd_variants)
            plan_id      = random.choice(PLAN_WEIGHTS_LIST) if PLAN_WEIGHTS_LIST else (plans[0]["id"] if plans else None)
            if not plan_id:
                continue

            # Create cart
            cart_resp = api_post("/api/carts", {
                "fluid_shop": fluid_shop,
                "country_code": "US",
                "cart": {
                    "customer_id": cid,
                    "ship_to_id": cdata["address_id"],
                    "currency_code": "USD",
                },
            })
            cart_token = cart_resp.get("cart", {}).get("cart_token", "")
            if not cart_token:
                sub_errors += 1
                continue

            # Add item to cart
            item_resp = api_post(f"/api/carts/{cart_token}/items", {
                "items": [{"variant_id": variant_info["variant_id"], "quantity": 1}],
            })
            if not item_resp.get("cart", {}).get("items"):
                sub_errors += 1
                continue

            # Create subscription
            days_out  = random.randint(3, 45)
            next_bill = (datetime.now() + timedelta(days=days_out)).strftime("%Y-%m-%d")
            sub_resp  = api_post("/api/subscriptions", {
                "subscription": {
                    "cart_token": cart_token,
                    "customer_id": cid,
                    "variant_id": variant_info["variant_id"],
                    "subscription_plan_id": plan_id,
                    "address_id": cdata["address_id"],
                    "payment_method_id": cdata["pm_id"],
                    "next_bill_date": next_bill,
                    "timezone": "America/New_York",
                },
            })
            sub = sub_resp.get("subscription", {})
            if sub.get("id"):
                sub_orders_created += 1
                cust_sub_count[cid] += 1
                if sub_orders_created % 10 == 0 or sub_orders_created <= 3:
                    print(f"  [{sub_orders_created}/{N_SUBS}] Sub {sub['id']}: "
                          f"{variant_info['title'][:30]} | "
                          f"next={next_bill}")
            else:
                sub_errors += 1
                if sub_errors <= 5:
                    print(f"  Sub error: {sub_resp.get('errors', sub_resp.get('error'))}")

            time.sleep(0.2)

        print(f"  Subscriptions created: {sub_orders_created} ({sub_errors} errors)")
elif N_SUBS > 0 and not fluid_shop:
    print(f"\n[5a/5] Skipping subscriptions (could not determine company shop slug)")
    print("  To enable subscriptions, run: fluid whoami and note the company subdomain")

# ── Phase 5b: Seed bulk orders ────────────────────────────────────────────────
BULK_ORDERS = ORDER_COUNT - sub_orders_created
print(f"\n[5b/5] Creating {BULK_ORDERS} bulk orders (with products)...")

# Build customer pool for orders (use all created customers)
all_cust_pool = []
for c in customers_to_create:
    # Match to internal ID via pm_data or fresh_customers lookup
    internal_id  = None
    addr_id      = None
    for fc in fresh_customers:
        if fc.get("external_integration_market_id") == c["ext_id"]:
            internal_id = fc["id"]
            break
    if internal_id and internal_id in pm_data:
        addr_id = pm_data[internal_id]["address_id"]
    all_cust_pool.append({
        "ext_id":   c["ext_id"],
        "first":    c["first"],
        "last":     c["last"],
        "email":    c["email"],
        "currency": c["currency"],
        "country":  c["country_code"],
        "ship_to":  c["address_attrs"],
    })

# Use stable demo identifiers so rerunning the skill updates the same bulk orders.
ORDER_PREFIX = "DEMO"

orders_payload = []
for i in range(BULK_ORDERS):
    cust = random.choice(all_cust_pool)
    currency = cust["currency"]
    available_variants = variants_by_currency.get(currency, usd_variants)

    num_items  = random.choices([1, 2, 3], weights=[50, 35, 15])[0]
    item_pool  = random.sample(available_variants, min(num_items, len(available_variants)))
    items      = []
    total      = 0.0
    for v in item_pool:
        qty = random.randint(1, 3)
        items.append({
            "product_sku": v["sku"],
            "name":        v["title"],
            "quantity":    qty,
            "unit_price":  v["price"],
        })
        total += v["price"] * qty

    total      = round(total, 2)
    shipping   = round(random.choice([0.0, 0.0, 5.99, 7.99, 9.99]), 2)
    grand_total = round(total + shipping, 2)

    fin_status = pick_status()
    src        = pick_source()
    order_index = i + 1
    order_num  = f"{ORDER_PREFIX}-{order_index:06d}"
    ext_id     = f"DEMO-ORDER-{order_index:06d}"

    order = {
        "external_id":                          ext_id,
        "customer_external_integration_market_id": cust["ext_id"],
        "email":                                cust["email"],
        "first_name":                           cust["first"],
        "last_name":                            cust["last"],
        "order_number":                         order_num,
        "amount":                               grand_total,
        "shipping_amount":                      shipping,
        "financial_status":                     fin_status,
        "order_status":                         "completed" if fin_status == "paid" else "pending",
        "sale_date":                            random_date(),
        "currency_code":                        currency,
        "source":                               src,
        "items":                                items,
        "ship_to": {
            "name":         f"{cust['first']} {cust['last']}",
            "address1":     cust["ship_to"]["address1"],
            "city":         cust["ship_to"]["city"],
            "state":        cust["ship_to"].get("state",""),
            "postal_code":  cust["ship_to"]["postal_code"],
            "country_code": cust["country"],
        },
    }

    # Add promo code to ~12% of orders
    if random.random() < PROMO_RATE:
        order["metadata"] = {"promo_code": random.choice(PROMO_CODES)}

    orders_payload.append(order)

bulk_created = 0
for i in range(0, len(orders_payload), BATCH_SIZE):
    batch = orders_payload[i:i+BATCH_SIZE]
    resp  = api_post("/api/v2/integrations/orders", {"orders": batch})
    batch_count = len(resp.get("orders", []))
    bulk_created += batch_count
    if (i // BATCH_SIZE) % 5 == 0:
        print(f"  [{bulk_created}/{BULK_ORDERS}] orders upserted...")
    if "errors" in resp and resp["errors"]:
        print(f"  Batch errors: {resp['errors']}")
    time.sleep(0.1)

# ── Done ──────────────────────────────────────────────────────────────────────
total_orders = sub_orders_created + bulk_created
print(f"\n{'=' * 60}")
print(f"DONE!")
print(f"  Customers created : {customers_created}")
print(f"  Subscriptions     : {sub_orders_created} (active, each generated 1 order)")
print(f"  Bulk orders       : {bulk_created}")
print(f"  Total orders      : {total_orders}")
print(f"  Target was        : {ORDER_COUNT}")
print(f"{'=' * 60}")
PYEOF
```

## 3. Substitute the order count

Before running the script, replace `ORDER_COUNT_PLACEHOLDER` in the script with the number the user gave. Use `sed` or inline replacement before execution:

```bash
# Example: replace placeholder with 300
sed 's/ORDER_COUNT_PLACEHOLDER/300/' the_script_above | FLUID_TOKEN=$(fluid-token) python3 -
```

Or just substitute manually in the heredoc before passing it to python3.

## 4. Report back

After the script finishes, report the summary to the user:
- Total orders seeded (bulk + subscription-generated)
- Number of active subscriptions created
- Number of customers created
- Link to check: `admin.fluid.app/orders` and `admin.fluid.app/subscriptions`

If the subscriptions were skipped (no `fluid_shop` discovered), explain how to fix it: switch to the company with `fluid switch "<Company Name>"` so the subdomain is known, then re-run.

## Important notes for this skill

- **Products must be imported first.** This skill uses existing active variants. If a product has no active variants with pricing, it won't appear in orders.
- **Product status `0` = active, `1` = draft** when using the integration import endpoint.
- **Subscriptions require USD customers** - the Bogus/dummy gateway is USD-only.
- **Cart items must be added separately** - create the cart first, then POST items to `/api/carts/:token/items` with `{"items": [...]}`. The initial cart creation does not accept items.
- **Order-to-product linking** uses `product_sku` in each item. Without a matching active variant, items get financial data but no product name.
- **This script is idempotent** via `external_id` upserts - re-running with the same seed creates/updates rather than duplicating orders.
