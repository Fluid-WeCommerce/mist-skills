# Theme Upload API Reference

Push locally built theme files to the Fluid theme system.

The active Fluid company is already selected in Mist Desktop, so none of these calls collect or pass a token — auth is injected by the runtime.

**Prefer `fluid theme push`.** The `fluid theme` CLI (authenticated to the active company) walks the working directory and uploads every resource — text files and binaries — in one command. Use the resource API below only as a fallback when you need fine-grained control over individual resources.

```bash
fluid theme push
```

## Step 1: Create or Find the Application Theme

### Create a new theme

```
fluid_api("/api/application_themes", "POST", {
  "application_theme": {
    "name": "My Clone Theme",
    "description": "Cloned from yellowbirdfoods.com",
    "status": "active"
  }
})
```

Response: `{ "application_theme": { "id": 55697, "name": "My Clone Theme", ... } }`

Save the `id` — this is your `themeId` for all subsequent uploads.

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
  "key": "sections/exact-hiya-hero/index.liquid",
  "content": "<style>\n  .eh-hero { ... }\n</style>\n\n<section class=\"eh-hero\" {{ section.fluid_attributes }}>\n  ...\n</section>\n\n{% schema %}\n...\n{% endschema %}"
})
```

The `key` maps directly to the theme directory structure:

| File path | Key |
|-----------|-----|
| `layouts/theme.liquid` | `layouts/theme.liquid` |
| `home_page/default/index.liquid` | `home_page/default/index.liquid` |
| `page/about/index.liquid` | `page/about/index.liquid` |
| `product/default/index.liquid` | `product/default/index.liquid` |
| `sections/exact-hiya-hero/index.liquid` | `sections/exact-hiya-hero/index.liquid` |
| `config/settings_schema.json` | `config/settings_schema.json` |
| `assets/product.js` | `assets/product.js` |

### Binary files (.png, .jpg, .woff2, .svg, etc.)

Binary files must be uploaded to the Fluid DAM first, then referenced:

```
# 1. Upload the binary with the dam_upload tool (never POST to upload.fluid.app yourself).
#    dam_upload(file="assets/logo.png", name="Theme Logo")
#    → { "asset": { "default_variant_url": "https://ik.imagekit.io/fluid/..." } }

# 2. Register as theme resource
fluid_api("/api/application_themes/{themeId}/resources", "PUT", {
  "key": "assets/logo.png",
  "dam_asset": "https://ik.imagekit.io/fluid/..."
})
```

## Step 3: Upload All Files

`fluid theme push` already does this end-to-end and is the preferred path. If you need to drive it yourself, process every file in the theme directory — call `fluid_api` for text resources, and the `dam_upload` tool for binaries, then register the returned URL:

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

        if ext in TEXT_EXTENSIONS:
            with open(filepath, 'r') as f:
                content = f.read()
            fluid_api(
                f"/api/application_themes/{THEME_ID}/resources",
                "PUT",
                {"key": key, "content": content},
            )
            print(f"[Upload] {key} — done")
        else:
            # Binary: call the dam_upload tool with the file path; read
            # asset.default_variant_url from the returned asset record.
            dam_url = dam_upload(file=filepath, name=fname)["asset"]["default_variant_url"]
            if dam_url:
                fluid_api(
                    f"/api/application_themes/{THEME_ID}/resources",
                    "PUT",
                    {"key": key, "dam_asset": dam_url},
                )
                print(f"[Upload] {key} (binary via DAM) — done")
            else:
                print(f"[Upload] {key} — DAM UPLOAD FAILED")
```

## Notes

- `PUT` is idempotent — uploading the same key twice overwrites the previous version
- Upload order doesn't matter — Fluid resolves references at render time
- The theme must have `status: "active"` to be visible on the storefront
- Config files (`settings_schema.json`, `settings_data.json`) are uploaded the same way as any text resource
