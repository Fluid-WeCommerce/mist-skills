# Batch DAM Upload

Upload images in bulk to the Fluid DAM. The active Fluid company is already selected in Mist Desktop, so DAM auth (ImageKit auth + registration + the company-scoped folder) is handled for you — you never collect or pass a token, and you never POST to `upload.fluid.app` yourself.

## Use the `dam_upload` tool — not curl

`dam_upload` takes either a public `url` or a project-sandbox `path` and
returns the asset record. To batch-upload, issue many `dam_upload` calls in
parallel in a single turn. Each result carries the DAM URL at
`asset.default_variant_url`.

```
dam_upload(path=".mist-desktop/attachments/hero.jpg",  name="hero-desktop")
dam_upload(path=".mist-desktop/attachments/team.png",  name="team-photo")
dam_upload(path="assets/icon-star.svg",                name="icon-star", tags="icon,ui")
# → each returns { "asset": { "default_variant_url": "https://ik.imagekit.io/fluid/.../hero-desktop_abc123.jpg", ... } }
```

### `dam_upload` arguments

| Arg | Required | Description |
|-----|----------|-------------|
| `url` | One of `url` or `path` | Public source URL fetched server-side through `external_asset_url`. |
| `path` | One of `url` or `path` | File inside the project sandbox (absolute or project-relative). |
| `name` | No | Display name for the DAM asset. Defaults to the file's basename. |
| `description` | No | Asset description shown in the DAM browser. |
| `tags` | No | Comma-separated tags (e.g. `"brand,hero,2026-launch"`). |
| `folder` | No | Override the ImageKit folder. Defaults to the company-scoped folder Fluid assigns. |
| `create_media` | No | When `true`, also create a Fluid Media resource (works for images, videos, PDFs). |

Read `asset.default_variant_url` from each result and use it in your section templates and `settings_data.json`.

## Remote source-site images

For a public source image or video, pass its remote URL directly:

```text
dam_upload(url="https://cdn.example.com/hero.mp4",
           name="homepage-hero-desktop",
           create_media=true)
```

Mist sends remote sources through the upload service's
`external_asset_url` field. Use `path` only for a file already inside the
project sandbox. As a CLI fallback, `fluid dam upload --url
<SOURCE_MEDIA_URL> --name <name>` uses the same server-side fetch path.

## Oversized assets

If the remote upload is rejected for size, fetch the asset into the sandbox
and chain `compress_media` → `dam_upload(path=...)`. `compress_media` writes a
sibling `<name>_compressed.<ext>` (video: H.264/AAC; image: q:v, optional
`width` downscale) and returns the new path. Record the initial failure and
compressed byte size; never silently omit the asset.
