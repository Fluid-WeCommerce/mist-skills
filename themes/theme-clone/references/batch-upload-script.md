# Batch DAM Upload

Upload images in bulk to the Fluid DAM. The active Fluid company is already selected in Mist Desktop, so DAM auth (ImageKit auth + registration + the company-scoped folder) is handled for you — you never collect or pass a token, and you never POST to `upload.fluid.app` yourself.

## Use `fluid assets upload` through `run_cli` — not curl

`run_cli fluid assets upload` takes either a public `--url` or a
project-sandbox file path and prints the asset record as JSON. To batch-upload,
issue many `run_cli` calls in parallel in a single turn. Each result carries
the DAM URL at `asset.default_variant_url`.

```
run_cli fluid assets upload .mist-desktop/attachments/hero.jpg --name hero-desktop
run_cli fluid assets upload .mist-desktop/attachments/team.png --name team-photo
run_cli fluid assets upload assets/icon-star.svg --name icon-star --tags icon,ui
# → each prints { "asset": { "default_variant_url": "https://ik.imagekit.io/fluid/.../hero-desktop_abc123.jpg", ... } }
```

### `fluid assets upload` arguments

| Arg | Required | Description |
|-----|----------|-------------|
| `--url <url>` | One of `--url` or a file | Public source URL fetched server-side through `external_asset_url`. |
| `<file>` | One of `--url` or a file | File inside the project sandbox (project-relative). |
| `--name` | No | Display name for the DAM asset. Defaults to the file's basename. |
| `--description` | No | Asset description shown in the DAM browser. |
| `--tags` | No | Comma-separated tags (e.g. `brand,hero,2026-launch`). |
| `--folder` | No | Override the ImageKit folder. Defaults to the company-scoped folder Fluid assigns. |
| `--create-media` | No | Also create a Fluid Media resource (works for images, videos, PDFs). |

Read `asset.default_variant_url` from each result and use it in your section templates and `settings_data.json`.

## Remote source-site images

For a public source image or video, pass its remote URL directly:

```text
run_cli fluid assets upload --url https://cdn.example.com/hero.mp4 --name homepage-hero-desktop --create-media
```

The CLI sends remote sources through the upload service's
`external_asset_url` field. Pass a file path only for a file already inside the
project sandbox.

## Oversized assets

If the remote upload is rejected for size, pass the same public URL to
`compress_media(url=...)`, then feed its returned `output_path` to
`run_cli fluid assets upload <output_path>`. Mist safely streams the source into a bounded temporary
sandbox file and removes that staging file after compression. `compress_media`
writes a `<name>_compressed.<ext>` result (video: H.264/AAC; image: q:v,
optional `width` downscale). Record the initial failure and compressed byte
size; never silently omit the asset.
