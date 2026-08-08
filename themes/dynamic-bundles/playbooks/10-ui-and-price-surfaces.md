# 10 — Rendering the picker, and every price on the page

Supersedes `03-theme-generation.md` on card rendering and price display. Everything here is
a defect found in the generated section on a live storefront (2026-08-07) and fixed.

---

## 1. One card per **product**, not per item

The generated section looped `group.bundle_group_items` and emitted one card per **item**.
When a group holds several variants of the same product, the shopper sees the same title and
the same parent image repeated — three "Fries" cards, two "Chili" cards.

**Required shape:**

1. Group items by **parent product id** (`item.product_id` — confirmed present on the drop).
2. Render **one card per product**.
3. Render a **variant sub-picker** only for products contributing more than one variant.
4. Labels come from the variant's own option values. **Never a hardcoded list** ("Small /
   Medium / Large") — that breaks the moment a vertical has capacities, colours or tiers.
5. Selecting product + option must resolve to exactly **one** `variant_id`, and that is what
   goes into `bundled_items`.

This is the generic shape for every vertical: colour swatches, capacity pills, tier buttons,
sizes. Same mechanic.

## 2. Use the variant's image

Cards used `item.product_image_url` (the parent) even where each variant carried its own.
Use the **variant** image, fall back to the parent only when absent, and **swap it when the
sub-picker changes**.

## 3. The anchor is never visually subordinate to the options

The anchor item — the thing the bundle is *named after* — rendered at **36×36** beside
~144px option thumbnails. It read as a footnote to its own bundle.

Fix: derive the anchor's size from **the same sizing token as the option grid** so the two
cannot drift apart. Observed good ratio: anchor ≈ 1.25× an option thumbnail (180px against
144px). Make this an explicit requirement, not a judgement call.

---

## 4. A bundle page is not one price

On the live page the host template composed **four** sections, only one of which was wired to
the selection engine; the PDP header rendered **no price at all**; and listing cards rendered
a scalar where a bundle needs a range.

### 4a. Inventory before wiring

Before touching any of them, enumerate **every** surface that shows a price:

- PDP header / hero
- each composed section on the product template
- sticky CTA / add-to-cart bars
- listing, collection and search cards
- cart page, cart drawer, mini-cart

Classify each one:

| Class | Treatment |
|---|---|
| must update live | subscribes to the engine's computed total |
| should show a range / "from" | server-rendered, cannot update — render a range |
| correct as-is | leave it |
| should not render a price | remove it |

### 4b. One computed source of truth

Live surfaces **subscribe to the engine's total**. Never a second parallel calculation — that
is exactly how two numbers on one page drift apart.

- Surfaces outside the section need an explicit **data-attribute hook**, not a cross-section
  CSS selector.
- Server-rendered surfaces that cannot update show a **range or "from"** price.
- **First paint must equal the default configuration**, or the page visibly flickers from a
  wrong number to the right one.
- Remember `price_range` reads **`$0.00`** for an all-fixed bundle (playbook 09 §5). Do not
  wire a surface to it without checking the bundle's pricing shape first.

### 4c. Acceptance

> No price anywhere on the page may contradict another price on the same page at the same
> moment — and page == cart == checkout.

Check it at the default configuration, after one upgrade, and after one downgrade.
