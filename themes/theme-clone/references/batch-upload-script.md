# Batch DAM Upload

Upload images in bulk to the Fluid DAM. The active Fluid company is already selected in Mist Desktop, so DAM auth (ImageKit auth + registration + the company-scoped folder) is handled for you — you never collect or pass a token, and you never POST to `upload.fluid.app` yourself.

## Use the `dam_upload` tool — not curl

`dam_upload` takes a **file inside the project sandbox** and returns the asset record. To batch-upload, **issue many `dam_upload` calls in parallel in a single turn** — that's the intended pattern for "upload these 20 images." Each result carries the DAM URL at `asset.default_variant_url`.

```
dam_upload(file=".mist-desktop/attachments/hero.jpg",  name="hero-desktop")
dam_upload(file=".mist-desktop/attachments/team.png",  name="team-photo")
dam_upload(file="assets/icon-star.svg",                name="icon-star", tags="icon,ui")
# → each returns { "asset": { "default_variant_url": "https://ik.imagekit.io/fluid/.../hero-desktop_abc123.jpg", ... } }
```

### `dam_upload` arguments

| Arg | Required | Description |
|-----|----------|-------------|
| `file` | Yes | Path to the file inside the project sandbox (absolute or project-relative). |
| `name` | No | Display name for the DAM asset. Defaults to the file's basename. |
| `description` | No | Asset description shown in the DAM browser. |
| `tags` | No | Comma-separated tags (e.g. `"brand,hero,2026-launch"`). |
| `folder` | No | Override the ImageKit folder. Defaults to the company-scoped folder Fluid assigns. |
| `create_media` | No | When `true`, also create a Fluid Media resource (works for images, videos, PDFs). |

Read `asset.default_variant_url` from each result and use it in your section templates and `settings_data.json`.

## Remote source-site images

`dam_upload` uploads a local file, so for an image hosted on the source CDN, either:

- **Fetch it into the sandbox first** (the `crawl` tool can pull page assets, or download the URL), then call `dam_upload` on the saved path; or
- **Use the CLI** `fluid dam upload --url <SOURCE_IMAGE_URL> --name <name>`, which fetches a remote URL directly (also accepts `--description`, `--tags`, `--folder`, `--create-media`).

## Oversized assets

If a file is too large for the upload service or to view inline, chain `compress_media` → `dam_upload`. `compress_media` writes a sibling `<name>_compressed.<ext>` (video: H.264/AAC; image: q:v, optional `width` downscale) and returns the new path to feed into `dam_upload`.
