---
name: Build and Share a Form
description: >-
  Create a standalone Fluid form through the API, activate it to mint its
  public share token, set embed access controls, hand back the share link and
  embed code, and read or export the responses. Use for a reseller application,
  an RSVP, a product-interest survey — any form shared by link or embed rather
  than shown at enrollment checkout.
icon: clipboard-list
---

# Build and Share a Form

Builds a standalone (`general`) Fluid form end to end: write its fields, publish it, hand the user a share link or embed snippet, and read what comes back. This is for a form shared by link or embed — not the enrollment checkout form, which appears after payment and is a different thing (see https://docs.fluid.app/guides/checkout-forms).

The active Fluid company is already selected in Mist Desktop. All Fluid API calls go through the `fluid_api(path, method, body)` tool, which targets the active company's Fluid API with the token already injected — you never collect, validate, or store a Fluid API token or store URL.

The canonical references are the guide https://docs.fluid.app/guides/build-and-share-a-form and the Forms API reference starting at https://docs.fluid.app/api-reference/forms/create-a-form. Endpoints are named inline below; `web_fetch` the guide or a reference page if you need a full parameter or response shape.

## Critical Rules

> **Never create the form as `active`.** Create it as a `draft`, then PUT its status to `active`. The public share token is minted on the transition to active — a form created directly as `active` is live but has no share link until you generate one.

> **Confirm with `human_in_the_loop` before you activate a form and before you revoke it.** Both change who can reach the form publicly.

> **`form_components` is a JSON-encoded string, not an array.** Encode the array of field objects into a string before sending it inside the `form` object.

> **To edit a live form, round-trip the element IDs.** Take each element's `id` from the create or update response's `form_components`, not from the list-elements call (which also lists deactivated elements). A component with an `id` updates that element in place; one without an `id` adds a new element; an element you leave out is deactivated, and its stored answers are kept.

> **`sensitive_info` is permission-gated.** Changing which fields are sensitive needs the forms manage-sensitive permission, or the request returns `422`. A `403` means the token lacks the forms view or update permission — report it and stop.

## Flow Overview

```
1. Gather inputs        — purpose, fields, and whether access should be restricted
2. Write the fields     — build the form_components array (element_type + settings)
3. Create a draft       — POST /api/forms, form_type "general", save id + element ids
4. Confirm + activate    — show the field list, confirm, then PUT status "active" (mints token)
5. Set access (optional) — PATCH embed_settings: domains, password, expiry, limit, require contact
6. Share                — GET embed_code, hand back share_url + embed snippet
7. Read responses       — GET respondents, or POST export_csv
8. Revoke (on request)  — DELETE revoke_token after confirmation
```

## Reference Files

- [references/forms-api.md](references/forms-api.md) — the Forms endpoints this skill uses, each with its method, path, one-line purpose, and reference-page link.

---

## Step 1: Gather Inputs

Ask what the form is for and what fields it should collect. There are no credentials to gather — the active company is already selected and `fluid_api` injects the token.

Collect:

1. **Purpose** — e.g. "reseller application", "event RSVP", "product-interest survey".
2. **Fields** — each field's label, type, and whether it's required. Use `steps` for a picker if that's clearer.
3. **Access** — should anyone with the link respond, or should it be restricted (allowed domains, a password, an expiry, a submission cap, or required contact)?

Check the available element types with `fluid_api("/api/forms/{form_id}/form_elements", "GET")` against any existing form, or read the element catalog in the [List form elements](https://docs.fluid.app/api-reference/forms/list-form-elements) reference.

## Step 2: Write the Fields

Each field is a component object with an `element_type` and its settings. Build the array, then JSON-encode it into the `form_components` string in Step 3.

- Set `is_form_field: true` on every component that collects an answer; leave it off structural blocks (headers, section labels).
- An identity field is an `input` whose `puck_type` names it (`legal_name`, `email`, `phone_number`, `date_of_birth`, …).
- Use `short_text_entry` / `long_text_entry` for free text, `multiple_choice_entry` (with `multiple_choice_options`) for a choice, `number_entry` for a number, `file_upload` for an upload.
- Mark a field `sensitive_info: true` to have Fluid mask its answers on read and export unless the caller holds the forms view-sensitive permission (good for tax IDs, government numbers).
- Mark a text field `case_sensitive: true` when capital letters matter (e.g. a referral code); it's stored on the field and returned in metadata for exports and integrations.

Example component array (encode this to a string for `form_components`):

```json
[
  { "element_type": "input", "puck_type": "legal_name", "label": "Business legal name", "required": true, "is_form_field": true },
  { "element_type": "input", "puck_type": "email", "label": "Contact email", "required": true, "is_form_field": true },
  { "element_type": "short_text_entry", "label": "Employer Identification Number (EIN)", "required": true, "sensitive_info": true, "is_form_field": true }
]
```

## Step 3: Create the Form as a Draft

Send the fields inside a `form` object, with `form_type: "general"` and `status: "draft"`. The API reads nothing outside `form`.

```
fluid_api("/api/forms", "POST", {
  "form": {
    "title": "Reseller application",
    "form_type": "general",
    "status": "draft",
    "form_components": "<the JSON-encoded component array from Step 2>"
  }
})
```

The response returns the form with its `id` and a `form_components` that now carries each element's `id`. Save both — you need the element IDs to edit fields later (Step 8 of the guide). See [Create a form](https://docs.fluid.app/api-reference/forms/create-a-form) for the full contract.

## Step 4: Confirm, Then Activate

Show the user the field list you created and confirm it's right. Then activate — the token is minted on this transition:

```
human_in_the_loop("Activate \"{title}\" and mint its public share link?")

fluid_api("/api/forms/{id}", "PUT", { "form": { "status": "active" } })
```

If, for any reason, the form is already active without a token (e.g. it was created `active`), mint one explicitly with [Generate a public token](https://docs.fluid.app/api-reference/forms/generate-a-public-token):

```
fluid_api("/api/forms/{id}/generate_token", "POST")
```

Generating a token later also **rotates** it: the old link stops working. Only do that on request (e.g. a leaked link), and confirm first.

## Step 5: Set Who Can Reach It (optional)

If the user asked to restrict access, send only the controls they want via [Update embed settings](https://docs.fluid.app/api-reference/forms/update-embed-settings):

```
fluid_api("/api/forms/{id}/embed_settings", "PATCH", {
  "embed_settings": {
    "allowed_domains": ["partners.example.com"],
    "expires_at": "2026-12-31T23:59:59Z",
    "max_submissions": 500,
    "require_contact": true
  }
})
```

- `allowed_domains` limits which sites may embed the form.
- `expires_at` closes it at a datetime; `max_submissions` closes it after a response count.
- `require_contact` asks each respondent to identify themselves.
- To password-protect it, send a `password`; send `remove_password: true` to clear it.

## Step 6: Share It

Once the form is active and has a token, get everything needed to publish it with [Get embed code](https://docs.fluid.app/api-reference/forms/get-embed-code):

```
fluid_api("/api/forms/{id}/embed_code", "GET")
```

Hand back the `share_url` (the link to send or post), and — if they want to embed it — the `embed_url`, `iframe_snippet`, and `script_snippet`. If this call reports the form has no public token, activate it or generate a token first (Step 4), then try again.

## Step 7: Read the Responses

List submissions with [List form respondents](https://docs.fluid.app/api-reference/forms/list-form-respondents), or pull everything with [Export form responses as CSV](https://docs.fluid.app/api-reference/forms/export-form-responses-as-csv):

```
fluid_api("/api/forms/{id}/respondents", "GET")
fluid_api("/api/forms/{id}/export_csv", "POST")
```

A sensitive field's answer comes back masked as `********` unless the caller holds the forms view-sensitive permission. Summarize the answers in a Markdown table; don't dump raw JSON at the user.

## Step 8: Turn Access Off (on request)

When the form has run its course, revoke its public token with [Revoke the public token](https://docs.fluid.app/api-reference/forms/revoke-the-public-token):

```
human_in_the_loop("Revoke public access to \"{title}\"? The share link and embed will stop working; existing responses are kept.")

fluid_api("/api/forms/{id}/revoke_token", "DELETE")
```

Activating the form again mints a fresh token.

## Output

Report the form's `id`, status, the `share_url` (and embed snippet if requested), the access controls you set, and a short summary of any responses read. Say plainly what changed.
