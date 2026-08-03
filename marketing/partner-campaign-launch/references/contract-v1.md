# Professional partner campaign contract v1

V1 produces a local, immutable review package for an approved coach,
trainer, gym, club, physical therapist, wellness professional, or selected
athlete/creator. It does not edit Portal screens or make remote writes.

## Identity

Canonicalize the campaign name by trimming and collapsing whitespace. Require
1–60 ASCII alphanumeric words separated by single spaces; punctuation and
non-ASCII names must be revised before launch. Lowercase it and replace spaces
with `-`. This mapping is bounded and collision-free after case normalization.

Require a positive integer `product_id` no larger than 999999999999 and a
profile segment id no longer than 40 characters. Derive:

- `campaign_slug = <bounded normalized name>`
- `campaign_key = <campaign_slug>:<product_id>:<partner_segment>`
- `campaign_instance_id = <campaign_slug>-p<product_id>-<partner_segment>`
- Portal block `LayoutWidget-partner-campaign-<campaign_instance_id>`
- children `TextWidget-partner-campaign-<campaign_instance_id>-copy` and
  `QuickShareWidget-partner-campaign-<campaign_instance_id>-share`
- banner name `<profile name_prefix>:<campaign_instance_id>`

Require `campaign_instance_id` to match `^[a-z0-9-]{1,120}$`.

## Immutable copy and rules

Freeze these six non-empty strings before confirmation:

- `portal_copy_title`
- `portal_copy_body`, ending with the profile's exact disclosure
- `quick_share_title`, exactly equal to the product title
- `banner_text`
- `banner_button_text`
- `banner_button_url`, exactly equal to the verified product URL

Grade every package:

- `EXACT_TARGET` — company subdomain, runtime Portal path/name/id, screen/anchor,
  and product match the verified inputs.
- `NO_MEDICAL_CLAIMS` — no diagnosis, treatment, cure, prevention, or guaranteed outcome.
- `NO_EARNINGS_CLAIMS` — no earnings, conversion, ROI, endorsement, or outcome promise.
- `NO_UNVERIFIED_OFFER` — no invented discount, trial, price, scarcity, stock, or window.
- `LOCAL_ONLY` — only immutable package files may be written.
- `NO_REMOTE_TOOLS` — workflow workers have no API, CLI, deploy, or publish tools.

An omitted partner page is `not_applicable`, not pass or fail. A validated page
has a redacted receipt but is not part of `EXACT_TARGET`. Storefront targeting is
profile-approved configuration for human review, not proof it is enabled live.

## Exact Portal block

`portal-block.preview.json` is exactly this shape, with placeholders replaced by
the immutable context and no `share_link` field:

```json
{
  "id": "LayoutWidget-partner-campaign-<campaign_instance_id>",
  "type": "LayoutWidget",
  "props": {
    "sectionLayout": "2c-left-wider",
    "children": [
      {
        "id": "TextWidget-partner-campaign-<campaign_instance_id>-copy",
        "type": "TextWidget",
        "columnIndex": 0,
        "props": { "title": "<portal_copy_title>", "description": "<portal_copy_body>" }
      },
      {
        "id": "QuickShareWidget-partner-campaign-<campaign_instance_id>-share",
        "type": "QuickShareWidget",
        "columnIndex": 1,
        "props": {
          "titleText": "<quick_share_title>",
          "shareableResource": {
            "id": 123,
            "type": "Product",
            "title": "<product_title>",
            "image_url": "<product_image_url>",
            "display_price": "<product_display_price>",
            "status": "<product_status>"
          }
        }
      }
    ]
  }
}
```

## Exact local banner payload

`storefront-banner.draft.json` has wrapper `{ "banner": { ... } }`, deterministic
name, `status:"draft"`, the profile's targeting and allowlisted styles, and:

```json
{
  "content": {
    "banner_text": "<banner_text>",
    "button_text": "<banner_button_text>",
    "button_url": "<verified product URL>"
  }
}
```

It is a review artifact, not an API request or proof of live availability.

## Package and idempotency

Canonical JSON means UTF-8, recursively sorted object keys, compact separators,
and array order preserved. The allowlisted `campaign-package.json` fields are:
schema version; campaign
identity; company/profile/Portal projections and tool receipts; optional redacted
partner-page receipt; product projection and tool receipt; immutable copy; exact
Portal block; exact banner payload; rules; limitations; and write ledger.
Never include raw API responses, tokens, cookies, email, or customer data.

For `campaign_package`, write only:

```text
.mist-campaigns/<campaign_instance_id>/campaign-package.json
.mist-campaigns/<campaign_instance_id>/portal-block.preview.json
.mist-campaigns/<campaign_instance_id>/storefront-banner.draft.json
.mist-campaigns/<campaign_instance_id>/release-checklist.md
```

Read before writing. If all four exact artifacts already exist and hash-match,
write nothing. If any path exists with different bytes, or only a subset exists,
stop; never overwrite or fill in partial state. `dry_run` writes nothing.

## Exact workflow context

Every key below is required. Empty strings are allowed only for partner-page
fields when `partner_page_status` is `not_applicable`.

| Key | Type / bound |
| --- | --- |
| `serialized_company_profile` | JSON string matching profile schema |
| `company_request_id` | non-secret Fluid GET request receipt |
| `company_subdomain` | 1–63 chars |
| `expected_portal_project_path` | runtime-resolved absolute path |
| `expected_portal_definition_name` | 1–120 chars |
| `expected_portal_definition_id` | positive integer |
| `portal_screen_path`, `portal_anchor_id`, `portal_screen_sha256` | safe relative path/id/hash |
| `run_mode` | `dry_run` or `campaign_package` |
| `build_campaign_package` | boolean equal to `run_mode==campaign_package` |
| `campaign_name`, `campaign_slug`, `campaign_key`, `campaign_instance_id` | identity contract above |
| `partner_segment`, `audience_noun`, `campaign_goal` | exact profile option values |
| `partner_page_status` | `not_applicable` or `validated` |
| `partner_page_initial_url`, `partner_page_final_url`, `approved_partner_identity`, `approved_partner_host`, `partner_page_evidence_receipt` | redacted page receipt strings |
| `portal_copy_title`, `portal_copy_body`, `quick_share_title` | immutable strings, max 1000 each |
| `banner_text`, `banner_button_text`, `banner_button_url`, `banner_name` | immutable strings, max 1000 each |
| `product_id` | positive integer ≤ 999999999999 |
| `product_title`, `product_url`, `product_image_url`, `product_display_price`, `product_status` | projected product facts |
| `product_verified_at`, `product_request_id` | ISO timestamp and non-secret Fluid GET receipt |
| `attribution_disclosure`, `rejected_message_summary` | approved strings |
| `serialized_portal_block`, `serialized_banner_payload`, `serialized_campaign_package` | exact JSON strings |
| `release_checklist_markdown` | exact deterministic checklist string |

Literal launcher shape:

```text
run_workflow({
  workflow_slug: "partner-campaign-preview",
  run_title: "Partner campaign — <campaign_name>",
  context: { <every key above exactly once; no extra keys> }
})
```

## Value boundary

The package proves verified catalog facts, deterministic campaign composition,
and a reviewable representation of proposed Portal/banner content. It does not
prove visible rendering, link minting, attribution, visits, conversion,
retention, rewards, ROI, native mobile, or a live release.
