#!/usr/bin/env node

import { createHash } from "node:crypto";
import {
  existsSync,
  readFileSync,
  realpathSync,
  statSync,
} from "node:fs";
import path from "node:path";
import process from "node:process";

const ROUTES = ["home", "shop", "pdp"];
const VIEWPORTS = {
  desktop: { width: 1440, height: 900 },
  mobile: { width: 390, height: 844 },
};
const HTML_PATTERN = /<(?:html|body|main|section|div)\b/i;
const MAX_BOUNDARY_AGE_MS = 30 * 60 * 1000;

function manifestArgument() {
  const index = process.argv.indexOf("--manifest");
  return index >= 0 && process.argv[index + 1]
    ? process.argv[index + 1]
    : "clone-manifest.json";
}

function parseTimestamp(value, label, errors) {
  if (
    typeof value !== "string" ||
    !value.trim() ||
    !/(?:Z|[+-]\d{2}:\d{2})$/i.test(value)
  ) {
    errors.push(`${label}: missing timezone-aware ISO-8601 timestamp`);
    return null;
  }
  const parsed = Date.parse(value);
  if (!Number.isFinite(parsed)) {
    errors.push(`${label}: invalid ISO-8601 timestamp ${JSON.stringify(value)}`);
    return null;
  }
  return parsed;
}

function safeProjectFile(projectRoot, rawPath, label, errors) {
  if (typeof rawPath !== "string" || !rawPath.trim()) {
    errors.push(`${label}: missing local path`);
    return null;
  }
  if (path.isAbsolute(rawPath) || rawPath.split(/[\\/]/).includes("..")) {
    errors.push(`${label}: path must stay inside the theme project`);
    return null;
  }
  const resolved = path.resolve(projectRoot, rawPath);
  const rootPrefix = `${path.resolve(projectRoot)}${path.sep}`;
  if (!resolved.startsWith(rootPrefix)) {
    errors.push(`${label}: path escapes the theme project`);
    return null;
  }
  if (!existsSync(resolved) || !statSync(resolved).isFile()) {
    errors.push(`${label}: file does not exist: ${rawPath}`);
    return null;
  }
  const canonical = realpathSync(resolved);
  if (!canonical.startsWith(rootPrefix)) {
    errors.push(`${label}: symlink escapes the theme project`);
    return null;
  }
  return canonical;
}

function sha256(filePath) {
  return createHash("sha256").update(readFileSync(filePath)).digest("hex");
}

function pngDimensions(filePath) {
  const header = readFileSync(filePath).subarray(0, 24);
  const signature = Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]);
  if (
    header.length !== 24 ||
    !header.subarray(0, 8).equals(signature) ||
    header.toString("ascii", 12, 16) !== "IHDR"
  ) {
    return null;
  }
  return {
    width: header.readUInt32BE(16),
    height: header.readUInt32BE(20),
  };
}

function validateReceipt(
  projectRoot,
  receipt,
  label,
  errors,
  minimumBytes = 1,
) {
  if (!receipt || typeof receipt !== "object" || Array.isArray(receipt)) {
    errors.push(`${label}: receipt must be an object`);
    return null;
  }
  const filePath = safeProjectFile(projectRoot, receipt.path, label, errors);
  if (!filePath) return null;
  if (!receipt.path.startsWith(".mist-desktop/source-baselines/")) {
    errors.push(`${label}: evidence must live in source-baselines`);
  }
  const actualBytes = statSync(filePath).size;
  const expectedBytes = receipt.bytes ?? receipt.byteLength;
  if (expectedBytes !== actualBytes) {
    errors.push(
      `${label}: byte count mismatch (manifest=${expectedBytes}, disk=${actualBytes})`,
    );
  }
  if (actualBytes < minimumBytes) {
    errors.push(`${label}: implausibly small file (${actualBytes} bytes)`);
  }
  if (typeof receipt.sha256 !== "string" || receipt.sha256.length !== 64) {
    errors.push(`${label}: missing 64-character sha256`);
  } else if (receipt.sha256.toLowerCase() !== sha256(filePath)) {
    errors.push(`${label}: sha256 mismatch`);
  }
  return filePath;
}

function canonicalUrl(value) {
  if (typeof value !== "string") return null;
  try {
    const parsed = new URL(value.trim());
    if (!["http:", "https:"].includes(parsed.protocol)) return null;
    parsed.hash = "";
    return parsed.toString();
  } catch {
    return null;
  }
}

function srcsetUrls(value) {
  if (typeof value !== "string") return [];
  return value
    .split(",")
    .map((part) => part.trim().split(/\s+/, 1)[0])
    .filter(Boolean);
}

function renderedMediaUrls(sidecar) {
  const urls = new Set();
  const media = sidecar?.rendered?.media;
  if (!Array.isArray(media)) return urls;
  for (const item of media) {
    if (!item || typeof item !== "object") continue;
    for (const key of ["currentSrc", "src", "poster"]) {
      const normalized = canonicalUrl(item[key]);
      if (normalized) urls.add(normalized);
    }
    if (!Array.isArray(item.sourceCandidates)) continue;
    for (const candidate of item.sourceCandidates) {
      if (!candidate || typeof candidate !== "object") continue;
      const normalized = canonicalUrl(candidate.src);
      if (normalized) urls.add(normalized);
      for (const value of srcsetUrls(candidate.srcset)) {
        const normalizedCandidate = canonicalUrl(value);
        if (normalizedCandidate) urls.add(normalizedCandidate);
      }
    }
  }
  return urls;
}

function manifestMediaUrls(manifest, errors) {
  const items = manifest?.priority_media?.items;
  if (!Array.isArray(items) || items.length === 0) {
    errors.push("priority_media.items: missing or empty");
    return new Set();
  }
  const urls = new Set();
  items.forEach((item, index) => {
    const label = `priority_media.items[${index}]`;
    if (!item || typeof item !== "object" || Array.isArray(item)) {
      errors.push(`${label}: item must be an object`);
      return;
    }
    const normalized = canonicalUrl(item.source_url);
    if (!normalized) {
      errors.push(`${label}: source_url must be an absolute HTTP(S) URL`);
    } else {
      urls.add(normalized);
    }
    const candidates = item.source_candidates ?? [];
    if (!Array.isArray(candidates)) {
      errors.push(`${label}: source_candidates must be an array`);
    } else {
      candidates.forEach((candidate, candidateIndex) => {
        const normalizedCandidate = canonicalUrl(candidate);
        if (!normalizedCandidate) {
          errors.push(
            `${label}.source_candidates[${candidateIndex}]: must be an absolute HTTP(S) URL`,
          );
        } else {
          urls.add(normalizedCandidate);
        }
      });
    }
    for (const key of ["route", "landmark", "viewport_role", "media_kind"]) {
      if (typeof item[key] !== "string" || !item[key].trim()) {
        errors.push(`${label}: missing ${key}`);
      }
    }
    if (item.media_kind === "video") {
      const playback = item.video_playback_attributes;
      if (!playback || typeof playback !== "object") {
        errors.push(`${label}: video playback attributes are missing`);
        return;
      }
      for (const key of ["autoplay", "loop", "muted", "playsinline"]) {
        if (typeof playback[key] !== "boolean") {
          errors.push(`${label}: video attribute ${key} must be boolean`);
        }
      }
    }
  });
  return urls;
}

function run() {
  const manifestPath = path.resolve(manifestArgument());
  const projectRoot = path.dirname(manifestPath);
  const errors = [];
  let manifest;
  try {
    manifest = JSON.parse(readFileSync(manifestPath, "utf8"));
  } catch (error) {
    console.log(`SOURCE_INVENTORY_VALIDATION: fail\n- manifest: ${error}`);
    return 1;
  }
  if (!manifest || typeof manifest !== "object" || Array.isArray(manifest)) {
    console.log(
      "SOURCE_INVENTORY_VALIDATION: fail\n- manifest root must be an object",
    );
    return 1;
  }

  const runStartedAt = parseTimestamp(
    manifest.evidence_run_started_at,
    "evidence_run_started_at",
    errors,
  );
  const visualRoutes =
    manifest.visual_routes &&
    typeof manifest.visual_routes === "object" &&
    !Array.isArray(manifest.visual_routes)
      ? manifest.visual_routes
      : {};
  if (Object.keys(visualRoutes).length === 0) {
    errors.push("visual_routes: missing object");
  }

  const capturedTimes = [];
  const allRenderedUrls = new Set();
  const evidenceFiles = new Set();

  for (const route of ROUTES) {
    const routeEntry = visualRoutes[route];
    if (!routeEntry || typeof routeEntry !== "object") {
      errors.push(`visual_routes.${route}: missing object`);
      continue;
    }
    if (typeof routeEntry.source_url !== "string") {
      errors.push(`visual_routes.${route}.source_url: missing`);
    }
    if (!Array.isArray(routeEntry.landmarks) || routeEntry.landmarks.length === 0) {
      errors.push(`visual_routes.${route}.landmarks: missing or empty`);
    }
    const sourceEvidence = routeEntry.source_evidence;
    if (!sourceEvidence || typeof sourceEvidence !== "object") {
      errors.push(`visual_routes.${route}.source_evidence: missing`);
      continue;
    }

    for (const [viewportName, expectedViewport] of Object.entries(VIEWPORTS)) {
      const label = `visual_routes.${route}.source_evidence.${viewportName}`;
      const cell = sourceEvidence[viewportName];
      if (!cell || typeof cell !== "object") {
        errors.push(`${label}: missing object`);
        continue;
      }
      const capturedAt = parseTimestamp(
        cell.captured_at,
        `${label}.captured_at`,
        errors,
      );
      if (capturedAt !== null) capturedTimes.push(capturedAt);
      if (JSON.stringify(cell.requested_viewport) !== JSON.stringify(expectedViewport)) {
        errors.push(
          `${label}: requested_viewport must be ${JSON.stringify(expectedViewport)}`,
        );
      }
      if (
        !Number.isInteger(cell.status) ||
        cell.status < 200 ||
        cell.status >= 400
      ) {
        errors.push(`${label}: status must be a successful HTTP status`);
      }
      if (typeof cell.final_url !== "string") {
        errors.push(`${label}: final_url is missing`);
      }
      if (typeof cell.overlay_handling !== "string") {
        errors.push(`${label}: overlay_handling is missing`);
      }

      const screenshot = validateReceipt(
        projectRoot,
        cell,
        `${label}.screenshot`,
        errors,
      );
      if (screenshot) {
        evidenceFiles.add(screenshot);
        const dimensions = pngDimensions(screenshot);
        if (!dimensions) {
          errors.push(`${label}: screenshot is not a valid PNG`);
        } else if (
          dimensions.width !== cell.width ||
          dimensions.height !== cell.height
        ) {
          errors.push(
            `${label}: decoded PNG dimensions ${JSON.stringify(dimensions)} do not match the manifest`,
          );
        }
      }
      if (cell.width !== expectedViewport.width) {
        errors.push(`${label}: decoded screenshot width is wrong`);
      }
      if (!Number.isInteger(cell.height) || cell.height < expectedViewport.height) {
        errors.push(`${label}: decoded screenshot height is too small`);
      }

      const sidecarPath = validateReceipt(
        projectRoot,
        cell.page_evidence,
        `${label}.page_evidence`,
        errors,
        200,
      );
      if (sidecarPath) {
        evidenceFiles.add(sidecarPath);
        let sidecar = {};
        try {
          sidecar = JSON.parse(readFileSync(sidecarPath, "utf8"));
        } catch (error) {
          errors.push(`${label}.page_evidence: invalid JSON: ${error}`);
        }
        for (const url of renderedMediaUrls(sidecar)) allRenderedUrls.add(url);
        const expectedScreenshot = {
          path: cell.path,
          sha256: cell.sha256,
          byteLength: cell.bytes,
          width: cell.width,
          height: cell.height,
        };
        if (
          JSON.stringify(sidecar.screenshot) !==
          JSON.stringify(expectedScreenshot)
        ) {
          errors.push(`${label}: sidecar screenshot receipt mismatch`);
        }
        if (
          JSON.stringify(sidecar.requestedViewport) !==
          JSON.stringify(expectedViewport)
        ) {
          errors.push(`${label}: sidecar viewport mismatch`);
        }
        if (sidecar.finalUrl !== cell.final_url) {
          errors.push(`${label}: sidecar final URL mismatch`);
        }
        if (sidecar.statusCode !== cell.status) {
          errors.push(`${label}: sidecar status mismatch`);
        }
        if (sidecar.capturedAt !== cell.captured_at) {
          errors.push(`${label}: sidecar capture time mismatch`);
        }
        if (!sidecar.rendered || typeof sidecar.rendered !== "object") {
          errors.push(`${label}: sidecar rendered evidence missing`);
        } else if (sidecar.rendered.mediaTruncated === true) {
          errors.push(`${label}: rendered media evidence is truncated`);
        }
      }

      const documents = cell.documents;
      if (!documents || typeof documents !== "object") {
        errors.push(`${label}.documents: missing object`);
        continue;
      }
      const htmlPath = validateReceipt(
        projectRoot,
        documents.html,
        `${label}.documents.html`,
        errors,
        500,
      );
      const markdownPath = validateReceipt(
        projectRoot,
        documents.markdown,
        `${label}.documents.markdown`,
        errors,
        100,
      );
      if (htmlPath) {
        evidenceFiles.add(htmlPath);
        if (!HTML_PATTERN.test(readFileSync(htmlPath, "utf8"))) {
          errors.push(`${label}.documents.html: no rendered markup found`);
        }
      }
      if (markdownPath) evidenceFiles.add(markdownPath);
    }
  }

  if (runStartedAt !== null && capturedTimes.length > 0) {
    const earliest = Math.min(...capturedTimes);
    if (earliest < runStartedAt) {
      errors.push("evidence_run_started_at is after the earliest capture");
    } else if (earliest - runStartedAt > MAX_BOUNDARY_AGE_MS) {
      errors.push(
        "evidence_run_started_at is stale: it must be within 30 minutes of the earliest capture",
      );
    }
  }

  const manifestUrls = manifestMediaUrls(manifest, errors);
  const missingUrls = [...allRenderedUrls]
    .filter((url) => !manifestUrls.has(url))
    .sort();
  if (missingUrls.length > 0) {
    errors.push(
      `priority_media.items misses ${missingUrls.length} rendered media URLs ` +
        `(first ${Math.min(20, missingUrls.length)}):\n    ` +
        missingUrls.slice(0, 20).join("\n    "),
    );
  }
  if (evidenceFiles.size !== 24) {
    errors.push(
      `expected 24 distinct evidence files, found ${evidenceFiles.size}`,
    );
  }

  if (errors.length > 0) {
    console.log("SOURCE_INVENTORY_VALIDATION: fail");
    for (const error of errors) console.log(`- ${error}`);
    return 1;
  }

  console.log("SOURCE_INVENTORY_VALIDATION: pass");
  console.log(
    JSON.stringify({
      evidence_files: evidenceFiles.size,
      manifest_media_urls: manifestUrls.size,
      manifest_sha256: sha256(manifestPath),
      rendered_media_urls: allRenderedUrls.size,
      videos: manifest.priority_media.items.filter(
        (item) => item.media_kind === "video",
      ).length,
    }),
  );
  return 0;
}

process.exitCode = run();
