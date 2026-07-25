# Theme Upload API Reference

Push locally built theme files to the Fluid theme system.

The active Fluid company is already selected in Mist Desktop, so none of these calls collect or pass a token — auth is injected by the runtime.

**Prefer `fluid theme push`.** The `fluid theme` CLI (authenticated to the active company)
walks the working directory and uploads supported resources in one command. Use the
resource API below only as a fallback for text resources. The text-resource endpoint does
not register arbitrary DAM URLs as binary theme files.

```bash
fluid theme push
```

## Step 1: Create or Find the Application Theme

### Create a new theme

```
fluid_api("/api/application_themes", "POST", {
  "application_theme": {
    "name": "My Clone Theme",
    "description": "Cloned from the source storefront"
  }
})
```

Response: `{ "application_theme": { "id": 55697, "name": "My Clone Theme", ... } }`

Save the `id` — this is your `themeId` for all subsequent uploads. A fresh company already
has one active Base theme, so creating another theme as `active` can fail with
`RecordNotUnique`. Create it without status, upload and verify, then activate it with:

```
fluid_api("/api/application_themes/{themeId}", "PATCH", {
  "application_theme": { "status": "active" }
})
```

### Find an existing theme

```
fluid_api("/api/application_themes", "GET")
```

Returns `{ "application_themes": [...] }`. Find the one you want and use its `id`.

## Step 2: Upload Theme Resources

Each file in the theme becomes a resource. The `key` is the file path relative to the theme root.

### Text files (.liquid, .css, .js, .json, .html, .txt)

```
fluid_api("/api/application_themes/{themeId}/resources", "PUT", {
  "key": "sections/editorial_hero/index.liquid",
  "content": "<section class=\"editorial-hero\" {{ section.fluid_attributes }}>...</section>\n\n{% schema %}\n...\n{% endschema %}"
})
```

The `key` maps directly to the theme directory structure:

| File path                              | Key                                    |
| -------------------------------------- | -------------------------------------- |
| `layouts/theme.liquid`                 | `layouts/theme.liquid`                 |
| `home_page/default/index.liquid`       | `home_page/default/index.liquid`       |
| `page/about/index.liquid`              | `page/about/index.liquid`              |
| `product/default/index.liquid`         | `product/default/index.liquid`         |
| `sections/editorial_hero/index.liquid` | `sections/editorial_hero/index.liquid` |
| `config/settings_schema.json`          | `config/settings_schema.json`          |
| `assets/product.js`                    | `assets/product.js`                    |

### Binary files (.png, .jpg, .woff2, etc.)

For a resource the theme references by URL, upload it with `dam_upload` and store the
returned `asset.default_variant_url` in `settings_data.json`, a section preset, or the
appropriate block setting. Do not send `{ "dam_asset": "<url>" }` to the theme resource
endpoint: live API verification returns 422 for that fallback shape.

SVG source that is safe and intentionally part of the theme may be uploaded as text
content. Brand/product photography and videos belong in the DAM.

## Step 3: Upload All Files

`fluid theme push` is the preferred path. If you need to drive the resource API yourself,
upload text files only. Resolve binary assets to DAM URLs in theme settings before this
loop:

```python
import os

THEME_ID = 55697
THEME_DIR = "/tmp/fluid-theme-yellowbirdfoods"

TEXT_EXTENSIONS = {'.liquid', '.css', '.js', '.json', '.html', '.txt', '.svg'}

for root, dirs, files in os.walk(THEME_DIR):
    for fname in files:
        if fname.startswith('.'):
            continue
        filepath = os.path.join(root, fname)
        key = os.path.relpath(filepath, THEME_DIR)
        ext = os.path.splitext(fname)[1].lower()

        if ext not in TEXT_EXTENSIONS:
            print(f"[Skip] {key} — upload to DAM and reference its URL in settings")
            continue
        with open(filepath, 'r') as f:
            content = f.read()
        fluid_api(
            f"/api/application_themes/{THEME_ID}/resources",
            "PUT",
            {"key": key, "content": content},
        )
        print(f"[Upload] {key} — done")
```

## Notes

- `PUT` is idempotent — uploading the same key twice overwrites the previous version
- Upload order doesn't matter — Fluid resolves references at render time
- Activate only after the upload and dev-preview checks pass
- Config files (`settings_schema.json`, `settings_data.json`) are uploaded the same way as any text resource
