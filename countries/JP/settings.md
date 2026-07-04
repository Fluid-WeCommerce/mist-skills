---
name: Japan country settings
description: Legal and commercial defaults for selling into Japan — consumption tax, currency, language, address, disclosures, APPI, and price-display rules.
icon: flag
category: countries
---

# Japan (JP) — country settings

Baseline the `open-country` workflow and the Japanese `compliance-manager` skill load for JP.

## VAT profile

- Name: `Consumption tax` (`消費税` — shōhizei)
- Standard rate: `10%`
- Reduced rate: `8%` — food and non-alcoholic beverages (excluding restaurant meals), newspapers with subscription contracts.
- Notes: since 2015, foreign digital-services providers to Japanese consumers must register and remit consumption tax. Physical-goods imports are subject to customs + consumption tax collected at the border. The **Qualified Invoice System (適格請求書等保存方式)** started October 2023 — B2B customers may require a compliant invoice.

## Currency

- Code: `JPY`
- Symbol: `¥` (or `￥` full-width). Placed BEFORE the amount, no space: `¥1,999`.
- **No decimal**: JPY has no minor currency unit — never display prices with decimal points (`¥19.99` is wrong; use `¥1,999` or `¥2,000`).
- Thousands separator: `,` (comma). Example: `¥1,234,567`.

## Language

- Primary: `ja` (Japanese).
- Widely spoken: `en` (English) — acceptable as a secondary storefront language for tourism-focused or expat-targeted stores; almost never as the only one for a general-market storefront.
- **Furigana** — phonetic reading of names — is expected on Japanese enrollment forms.

## Address format

Example (realistic):

```
田中 太郎
〒150-0002
東京都渋谷区渋谷1-2-3
渋谷ビル5F
日本
```

In roman:

```
Taro Tanaka
150-0002
1-2-3 Shibuya, Shibuya-ku
Tokyo, Japan
```

Rules:

- **Address order is reversed:** in Japanese, addresses go from largest (prefecture) to smallest (building). Roman conversions reverse it back to Western order.
- Postal code prefix `〒` followed by 7 digits with a hyphen — `〒150-0002`.
- Prefecture (都道府県) — Tokyo (東京都), Osaka (大阪府), Hokkaido (北海道), or 43 prefectures ending in `県`.
- Ward (区) / city (市) / town (町) / village (村) hierarchy.
- Names are typically collected with **furigana** — phonetic reading in katakana or hiragana — so the storefront can pronounce names correctly.

## Mandatory disclosure pages

Every consumer-facing Japanese storefront must publish (**特定商取引法 — Act on Specified Commercial Transactions, ASCT**) the following. This is legally required, non-optional:

1. **特定商取引法に基づく表記** (Notation based on the ASCT) — a dedicated page listing:
   - Seller's legal name and representative's name.
   - Address (physical, not PO box).
   - Phone number.
   - Email address for customer inquiries.
   - Sale price and any additional fees (shipping, handling).
   - Method and timing of payment.
   - Method and timing of delivery.
   - Returns / exchange / refund policy (including who bears return shipping).
2. **プライバシーポリシー** (Privacy Policy) — APPI-compliant.
3. **利用規約** (Terms of Service).
4. **クッキーポリシー** — often bundled with the Privacy Policy.
5. **配送について** — shipping information.

The 特定商取引法に基づく表記 page is the single most-scrutinized page in JP e-commerce. Missing it is grounds for takedown by Japanese payment processors (many will refuse to onboard a store without one).

## Consumer protection basics

- Cooling-off period: **no unconditional distance-selling cooling-off period** for standard e-commerce. Door-to-door and multi-level marketing have specific cooling-off windows (typically 8-20 days depending on transaction type). Under the ASCT, refund and return terms are contractual — whatever the storefront publishes on 特定商取引法に基づく表記 is what customers can rely on. Publishing "no returns" is legal only when clearly and prominently disclosed.
- Refund window: contractually defined; must match what's on 特定商取引法に基づく表記.
- Warranty: implicit fitness under Civil Code Articles 562-566 (revised 2020) — non-conformity of goods gives the buyer rights to repair, replacement, price reduction, or refund.
- Cross-border obligations: NFR into JP — Japan Post / private couriers collect customs + consumption tax at delivery for shipments above the ¥16,666 de minimis for consumption tax purposes.

## Cookie / privacy law

- Framework: **APPI** (Act on the Protection of Personal Information) — as amended April 2022, effective April 2023, expanded rights and cross-border transfer restrictions.
- Cookie: APPI 2022 amendments treat "personal-related information" (personally-referable information like cookie IDs that become PII when combined with other data) with specific rules. Non-essential cookie use requires transparency about purposes and third parties. A cookie banner with opt-in is not strictly mandatory but is increasingly standard practice.
- Cross-border transfers: APPI Article 28 requires either consent or an adequacy finding for transfers to third countries. Explicit disclosure of the recipient country and safeguards is required.
- Regulator: **PPC** (Personal Information Protection Commission).

## Price display rule

- **Total-price display** (`総額表示`) — since April 2021, consumer prices in Japan MUST be shown as the total price INCLUDING consumption tax. Displaying only the ex-tax price is prohibited for B2C.
- Common formats: `¥1,100 (税込)` — where `税込` means "tax included". Both the total and the ex-tax + tax breakdown may be shown together as long as the total is clear.
- Shipping is not required to be in the sticker price but must be disclosed before order confirmation.

## Unit-price rule

**Limited.** No general online unit-price mandate. Some food-labeling requirements under the Food Sanitation Act apply to physical retail. Score online unit-price displays as `ok` when present, `review` when absent for JP.
