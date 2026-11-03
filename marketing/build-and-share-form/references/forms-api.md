# Forms API Reference

> **All calls go through the `fluid_api` tool** — `fluid_api(path, method, body)` with a
> RELATIVE path (e.g. `/api/forms`). The token and active company are injected
> automatically; never use raw fetch/curl or collect an API key.

All endpoints are paths on the active company's Fluid API. Reading needs the forms view permission; writing needs the forms update permission. A `403` means the token lacks the permission — report it and stop. For full parameters and responses, open the linked reference page or read the guide at https://docs.fluid.app/guides/build-and-share-a-form.

## Build and publish

| Method | Endpoint | Purpose | Reference |
| ------ | -------- | ------- | --------- |
| POST   | `/api/forms` | Create a form. Body is `{ "form": { ... } }`; `form_components` is a JSON-encoded string. | https://docs.fluid.app/api-reference/forms/create-a-form |
| PUT    | `/api/forms/{id}` | Update a form. Send only what changes (e.g. `{ "form": { "status": "active" } }`). Status → `active` mints the public token. | https://docs.fluid.app/api-reference/forms/update-a-form |
| POST   | `/api/forms/{id}/generate_token` | Mint or rotate the public token. Rotating kills the old link. | https://docs.fluid.app/api-reference/forms/generate-a-public-token |
| DELETE | `/api/forms/{id}/revoke_token` | Revoke public access. Existing responses are kept. | https://docs.fluid.app/api-reference/forms/revoke-the-public-token |

## Access and sharing

| Method | Endpoint | Purpose | Reference |
| ------ | -------- | ------- | --------- |
| PATCH  | `/api/forms/{id}/embed_settings` | Restrict access: `allowed_domains`, `password`/`remove_password`, `expires_at`, `max_submissions`, `require_contact`. Send only the controls you want. | https://docs.fluid.app/api-reference/forms/update-embed-settings |
| GET    | `/api/forms/{id}/embed_code` | Get `share_url`, `embed_url`, `iframe_snippet`, `script_snippet`. Requires a public token first. | https://docs.fluid.app/api-reference/forms/get-embed-code |

## Read

| Method | Endpoint | Purpose | Reference |
| ------ | -------- | ------- | --------- |
| GET    | `/api/forms` | List the company's forms. | https://docs.fluid.app/api-reference/forms/list-forms |
| GET    | `/api/forms/{id}/respondents` | List respondents and their answers. Sensitive answers are masked unless permitted. | https://docs.fluid.app/api-reference/forms/list-form-respondents |
| POST   | `/api/forms/{id}/export_csv` | Export responses as CSV. | https://docs.fluid.app/api-reference/forms/export-form-responses-as-csv |
| GET    | `/api/forms/{form_id}/form_elements` | Read the element types (for reference; use the create/update response for round-tripping IDs). | https://docs.fluid.app/api-reference/forms/list-form-elements |

## Element settings (inside each `form_components` entry)

- `element_type` — the field type: `input` (with a `puck_type` such as `legal_name`, `email`, `phone_number`, `date_of_birth`), `short_text_entry`, `long_text_entry`, `number_entry`, `multiple_choice_entry` (with `multiple_choice_options`), `yes_no_entry`, `checkbox`, `file_upload`, plus structural blocks (header, section_label, …).
- `label`, `placeholder`, `required` — the usual per-field settings.
- `is_form_field: true` — set on every component that collects an answer.
- `sensitive_info: true` — mask this field's answers on read/export unless the caller holds forms view-sensitive; changing it needs forms manage-sensitive (else `422`).
- `case_sensitive: true` — stored on a typed-text field and returned in metadata so exports and integrations treat capital letters as distinct; the API does not act on it.
- `id` — present only after the first save. Round-trip it from the create/update response to edit a field in place.
