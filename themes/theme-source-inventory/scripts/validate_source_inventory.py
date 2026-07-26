#!/usr/bin/env python3
"""Validate a Fluid theme source-inventory manifest using only the stdlib."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit, urlunsplit

ROUTES = ("home", "shop", "pdp")
VIEWPORTS = {
    "desktop": {"width": 1440, "height": 900},
    "mobile": {"width": 390, "height": 844},
}
HTML_PATTERN = re.compile(r"<(?:html|body|main|section|div)\b", re.IGNORECASE)
MAX_BOUNDARY_AGE = timedelta(minutes=30)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", default="clone-manifest.json")
    return parser.parse_args()


def parse_timestamp(value: Any, label: str, errors: list[str]) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{label}: missing ISO-8601 timestamp")
        return None
    try:
        normalized = value.replace("Z", "+00:00")
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        errors.append(f"{label}: invalid ISO-8601 timestamp {value!r}")
        return None
    if parsed.tzinfo is None:
        errors.append(f"{label}: timestamp must include a timezone")
        return None
    return parsed.astimezone(timezone.utc)


def safe_project_file(
    project_root: Path,
    raw_path: Any,
    label: str,
    errors: list[str],
) -> Path | None:
    if not isinstance(raw_path, str) or not raw_path.strip():
        errors.append(f"{label}: missing local path")
        return None
    relative = Path(raw_path)
    if relative.is_absolute() or ".." in relative.parts:
        errors.append(f"{label}: path must stay inside the theme project")
        return None
    resolved = (project_root / relative).resolve()
    try:
        resolved.relative_to(project_root.resolve())
    except ValueError:
        errors.append(f"{label}: path escapes the theme project")
        return None
    if not resolved.is_file():
        errors.append(f"{label}: file does not exist: {raw_path}")
        return None
    return resolved


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def png_dimensions(path: Path) -> tuple[int, int] | None:
    with path.open("rb") as handle:
        header = handle.read(24)
    if len(header) != 24 or header[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    if header[12:16] != b"IHDR":
        return None
    return struct.unpack(">II", header[16:24])


def validate_receipt(
    project_root: Path,
    receipt: Any,
    label: str,
    errors: list[str],
    *,
    minimum_bytes: int = 1,
) -> Path | None:
    if not isinstance(receipt, dict):
        errors.append(f"{label}: receipt must be an object")
        return None
    path = safe_project_file(project_root, receipt.get("path"), label, errors)
    if path is None:
        return None
    raw_path = str(receipt["path"])
    if not raw_path.startswith(".mist-desktop/source-baselines/"):
        errors.append(f"{label}: evidence must live in source-baselines")
    actual_bytes = path.stat().st_size
    expected_bytes = receipt.get("bytes", receipt.get("byteLength"))
    if expected_bytes != actual_bytes:
        errors.append(
            f"{label}: byte count mismatch (manifest={expected_bytes}, disk={actual_bytes})"
        )
    if actual_bytes < minimum_bytes:
        errors.append(f"{label}: implausibly small file ({actual_bytes} bytes)")
    expected_sha = receipt.get("sha256")
    actual_sha = sha256(path)
    if not isinstance(expected_sha, str) or len(expected_sha) != 64:
        errors.append(f"{label}: missing 64-character sha256")
    elif expected_sha.lower() != actual_sha:
        errors.append(f"{label}: sha256 mismatch")
    return path


def canonical_url(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    value = value.strip()
    if not value.lower().startswith(("http://", "https://")):
        return None
    parsed = urlsplit(value)
    return urlunsplit(
        (
            parsed.scheme.lower(),
            parsed.netloc.lower(),
            parsed.path,
            parsed.query,
            "",
        )
    )


def srcset_urls(value: Any) -> list[str]:
    if not isinstance(value, str):
        return []
    return [part.strip().split(" ", 1)[0] for part in value.split(",") if part.strip()]


def rendered_media_urls(sidecar: dict[str, Any]) -> set[str]:
    urls: set[str] = set()
    rendered = sidecar.get("rendered")
    if not isinstance(rendered, dict):
        return urls
    media = rendered.get("media")
    if not isinstance(media, list):
        return urls
    for item in media:
        if not isinstance(item, dict):
            continue
        for key in ("currentSrc", "src", "poster"):
            normalized = canonical_url(item.get(key))
            if normalized:
                urls.add(normalized)
        candidates = item.get("sourceCandidates")
        if not isinstance(candidates, list):
            continue
        for candidate in candidates:
            if not isinstance(candidate, dict):
                continue
            normalized = canonical_url(candidate.get("src"))
            if normalized:
                urls.add(normalized)
            for value in srcset_urls(candidate.get("srcset")):
                normalized = canonical_url(value)
                if normalized:
                    urls.add(normalized)
    return urls


def manifest_media_urls(manifest: dict[str, Any], errors: list[str]) -> set[str]:
    priority_media = manifest.get("priority_media")
    items = priority_media.get("items") if isinstance(priority_media, dict) else None
    if not isinstance(items, list) or not items:
        errors.append("priority_media.items: missing or empty")
        return set()

    urls: set[str] = set()
    for index, item in enumerate(items):
        label = f"priority_media.items[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{label}: item must be an object")
            continue
        normalized = canonical_url(item.get("source_url"))
        if normalized is None:
            errors.append(f"{label}: source_url must be an absolute HTTP(S) URL")
        else:
            urls.add(normalized)
        for key in ("route", "landmark", "viewport_role", "media_kind"):
            if not isinstance(item.get(key), str) or not item[key].strip():
                errors.append(f"{label}: missing {key}")
        if item.get("media_kind") == "video":
            playback = item.get("video_playback_attributes")
            if not isinstance(playback, dict):
                errors.append(f"{label}: video playback attributes are missing")
                continue
            for key in ("autoplay", "loop", "muted", "playsinline"):
                if not isinstance(playback.get(key), bool):
                    errors.append(f"{label}: video attribute {key} must be boolean")
    return urls


def validate() -> int:
    args = parse_args()
    manifest_path = Path(args.manifest).resolve()
    project_root = manifest_path.parent
    errors: list[str] = []

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"SOURCE_INVENTORY_VALIDATION: fail\n- manifest: {error}")
        return 1
    if not isinstance(manifest, dict):
        print("SOURCE_INVENTORY_VALIDATION: fail\n- manifest root must be an object")
        return 1

    run_started_at = parse_timestamp(
        manifest.get("evidence_run_started_at"),
        "evidence_run_started_at",
        errors,
    )
    visual_routes = manifest.get("visual_routes")
    if not isinstance(visual_routes, dict):
        errors.append("visual_routes: missing object")
        visual_routes = {}

    captured_times: list[datetime] = []
    all_rendered_urls: set[str] = set()
    evidence_files: set[Path] = set()

    for route in ROUTES:
        route_entry = visual_routes.get(route)
        if not isinstance(route_entry, dict):
            errors.append(f"visual_routes.{route}: missing object")
            continue
        if not isinstance(route_entry.get("source_url"), str):
            errors.append(f"visual_routes.{route}.source_url: missing")
        landmarks = route_entry.get("landmarks")
        if not isinstance(landmarks, list) or not landmarks:
            errors.append(f"visual_routes.{route}.landmarks: missing or empty")
        source_evidence = route_entry.get("source_evidence")
        if not isinstance(source_evidence, dict):
            errors.append(f"visual_routes.{route}.source_evidence: missing")
            continue

        for viewport_name, expected_viewport in VIEWPORTS.items():
            label = f"visual_routes.{route}.source_evidence.{viewport_name}"
            cell = source_evidence.get(viewport_name)
            if not isinstance(cell, dict):
                errors.append(f"{label}: missing object")
                continue
            captured_at = parse_timestamp(cell.get("captured_at"), f"{label}.captured_at", errors)
            if captured_at:
                captured_times.append(captured_at)
            if cell.get("requested_viewport") != expected_viewport:
                errors.append(
                    f"{label}: requested_viewport must be {expected_viewport}"
                )
            if not isinstance(cell.get("status"), int) or not 200 <= cell["status"] < 400:
                errors.append(f"{label}: status must be a successful HTTP status")
            if not isinstance(cell.get("final_url"), str):
                errors.append(f"{label}: final_url is missing")
            if not isinstance(cell.get("overlay_handling"), str):
                errors.append(f"{label}: overlay_handling is missing")
            screenshot = validate_receipt(project_root, cell, f"{label}.screenshot", errors)
            if screenshot:
                evidence_files.add(screenshot)
                dimensions = png_dimensions(screenshot)
                if dimensions is None:
                    errors.append(f"{label}: screenshot is not a valid PNG")
                elif dimensions != (cell.get("width"), cell.get("height")):
                    errors.append(
                        f"{label}: decoded PNG dimensions {dimensions} do not match "
                        f"the manifest {(cell.get('width'), cell.get('height'))}"
                    )
            if cell.get("width") != expected_viewport["width"]:
                errors.append(f"{label}: decoded screenshot width is wrong")
            if not isinstance(cell.get("height"), int) or cell["height"] < expected_viewport["height"]:
                errors.append(f"{label}: decoded screenshot height is too small")

            sidecar_path = validate_receipt(
                project_root,
                cell.get("page_evidence"),
                f"{label}.page_evidence",
                errors,
                minimum_bytes=200,
            )
            if sidecar_path:
                evidence_files.add(sidecar_path)
                try:
                    sidecar = json.loads(sidecar_path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError) as error:
                    errors.append(f"{label}.page_evidence: invalid JSON: {error}")
                    sidecar = {}
                if isinstance(sidecar, dict):
                    all_rendered_urls.update(rendered_media_urls(sidecar))
                    sidecar_screenshot = sidecar.get("screenshot")
                    expected_screenshot = {
                        "path": cell.get("path"),
                        "sha256": cell.get("sha256"),
                        "byteLength": cell.get("bytes"),
                        "width": cell.get("width"),
                        "height": cell.get("height"),
                    }
                    if sidecar_screenshot != expected_screenshot:
                        errors.append(f"{label}: sidecar screenshot receipt mismatch")
                    if sidecar.get("requestedViewport") != expected_viewport:
                        errors.append(f"{label}: sidecar viewport mismatch")
                    if sidecar.get("finalUrl") != cell.get("final_url"):
                        errors.append(f"{label}: sidecar final URL mismatch")
                    if sidecar.get("statusCode") != cell.get("status"):
                        errors.append(f"{label}: sidecar status mismatch")
                    if sidecar.get("capturedAt") != cell.get("captured_at"):
                        errors.append(f"{label}: sidecar capture time mismatch")
                    rendered = sidecar.get("rendered")
                    if not isinstance(rendered, dict):
                        errors.append(f"{label}: sidecar rendered evidence missing")
                    elif rendered.get("mediaTruncated") is True:
                        errors.append(f"{label}: rendered media evidence is truncated")

            documents = cell.get("documents")
            if not isinstance(documents, dict):
                errors.append(f"{label}.documents: missing object")
                continue
            html_path = validate_receipt(
                project_root,
                documents.get("html"),
                f"{label}.documents.html",
                errors,
                minimum_bytes=500,
            )
            markdown_path = validate_receipt(
                project_root,
                documents.get("markdown"),
                f"{label}.documents.markdown",
                errors,
                minimum_bytes=100,
            )
            if html_path:
                evidence_files.add(html_path)
                html = html_path.read_text(encoding="utf-8", errors="replace")
                if HTML_PATTERN.search(html) is None:
                    errors.append(f"{label}.documents.html: no rendered markup found")
            if markdown_path:
                evidence_files.add(markdown_path)

    if run_started_at and captured_times:
        earliest = min(captured_times)
        if earliest < run_started_at:
            errors.append("evidence_run_started_at is after the earliest capture")
        elif earliest - run_started_at > MAX_BOUNDARY_AGE:
            errors.append(
                "evidence_run_started_at is stale: it must be within 30 minutes "
                "of the earliest capture"
            )

    manifest_urls = manifest_media_urls(manifest, errors)
    missing_urls = sorted(all_rendered_urls - manifest_urls)
    if missing_urls:
        preview = "\n    ".join(missing_urls[:20])
        errors.append(
            f"priority_media.items misses {len(missing_urls)} rendered media URLs "
            f"(first {min(20, len(missing_urls))}):\n    {preview}"
        )
    if len(evidence_files) != 24:
        errors.append(
            f"expected 24 distinct evidence files, found {len(evidence_files)}"
        )

    if errors:
        print("SOURCE_INVENTORY_VALIDATION: fail")
        for error in errors:
            print(f"- {error}")
        return 1

    manifest_sha = sha256(manifest_path)
    print("SOURCE_INVENTORY_VALIDATION: pass")
    print(
        json.dumps(
            {
                "manifest_sha256": manifest_sha,
                "evidence_files": len(evidence_files),
                "rendered_media_urls": len(all_rendered_urls),
                "manifest_media_urls": len(manifest_urls),
                "videos": sum(
                    1
                    for item in manifest["priority_media"]["items"]
                    if item.get("media_kind") == "video"
                ),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(validate())
