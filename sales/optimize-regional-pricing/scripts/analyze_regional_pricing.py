#!/usr/bin/env python3
"""Build a deterministic, local regional-pricing scenario report."""

from __future__ import annotations

import argparse
import csv
import html
import json
import math
import mimetypes
import re
import sys
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen


REQUIRED_COLUMNS = {
    "market_id",
    "market_name",
    "currency",
    "visitors",
    "orders",
    "refunds",
    "current_local_price",
    "proposed_local_price",
    "usd_per_local",
    "lift_low_pct",
    "lift_base_pct",
    "lift_high_pct",
    "assumption_basis",
    "assumption_note",
}

OPTIONAL_DEFAULTS = {
    "tax_inclusive_pct": "0",
    "payment_fee_pct": "0",
    "payment_fee_fixed_usd": "0",
    "variable_cost_usd": "0",
}

SCENARIOS = ("low", "base", "high")
MAX_IMAGE_BYTES = 8 * 1024 * 1024
MAX_PRODUCT_PAGE_BYTES = 2 * 1024 * 1024


class InputError(ValueError):
    pass


class ProductImageMetaParser(HTMLParser):
    """Collect official preview-image candidates from product-page metadata."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.candidates: list[str] = []

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        attributes = {
            key.lower(): (value or "").strip()
            for key, value in attrs
        }
        if tag.lower() == "meta":
            key = (
                attributes.get("property")
                or attributes.get("name")
                or ""
            ).lower()
            if key in {
                "og:image",
                "og:image:url",
                "og:image:secure_url",
                "twitter:image",
                "twitter:image:src",
            }:
                candidate = attributes.get("content", "")
                if candidate:
                    self.candidates.append(candidate)
        elif tag.lower() == "link":
            rel = {
                item.lower()
                for item in attributes.get("rel", "").split()
            }
            candidate = attributes.get("href", "")
            if "image_src" in rel and candidate:
                self.candidates.append(candidate)


def validate_web_url(value: str, label: str) -> str:
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise InputError(f"{label} must be an http or https URL")
    if parsed.username or parsed.password:
        raise InputError(f"{label} must not contain embedded credentials")
    return value


def fetch_bytes(url: str, max_bytes: int, accept: str) -> tuple[bytes, str, str]:
    validate_web_url(url, "image source")
    request = Request(
        url,
        headers={
            "Accept": accept,
            "User-Agent": "RegionalPricingReport/1.0",
        },
    )
    try:
        with urlopen(request, timeout=15) as response:
            final_url = response.geturl()
            validate_web_url(final_url, "redirected image source")
            content_type = (response.headers.get_content_type() or "").lower()
            declared_length = response.headers.get("Content-Length")
            if declared_length and int(declared_length) > max_bytes:
                raise InputError(f"remote asset exceeds {max_bytes // 1024 // 1024} MB")
            payload = response.read(max_bytes + 1)
    except (HTTPError, URLError, OSError, ValueError) as exc:
        raise InputError(f"could not fetch {url}: {exc}") from exc
    if len(payload) > max_bytes:
        raise InputError(f"remote asset exceeds {max_bytes // 1024 // 1024} MB")
    return payload, content_type, final_url


def extract_product_image_url(page_html: bytes, page_url: str) -> str | None:
    parser = ProductImageMetaParser()
    parser.feed(page_html.decode("utf-8", errors="replace"))
    for candidate in parser.candidates:
        resolved = urljoin(page_url, candidate)
        try:
            return validate_web_url(resolved, "product image metadata")
        except InputError:
            continue
    return None


def image_extension(payload: bytes, content_type: str, source: str) -> str:
    head = payload[:512].lstrip()
    if payload.startswith(b"\x89PNG\r\n\x1a\n"):
        return ".png"
    if payload.startswith(b"\xff\xd8\xff"):
        return ".jpg"
    if payload.startswith((b"GIF87a", b"GIF89a")):
        return ".gif"
    if payload.startswith(b"RIFF") and payload[8:12] == b"WEBP":
        return ".webp"
    if len(payload) >= 12 and payload[4:8] == b"ftyp" and payload[8:12] in {
        b"avif",
        b"avis",
    }:
        return ".avif"
    if head.startswith(b"<svg") or (
        head.startswith(b"<?xml") and b"<svg" in head
    ):
        return ".svg"
    guessed = mimetypes.guess_extension(content_type) if content_type else None
    if guessed == ".jpe":
        guessed = ".jpg"
    raise InputError(
        f"product image {source!r} is not a supported PNG, JPEG, GIF, WebP, AVIF, or SVG"
        + (f" ({content_type})" if content_type else "")
    )


def prepare_image_asset(
    *,
    explicit_source: str,
    product_url: str,
    alt: str,
    default_alt: str,
    source_label: str,
    base_dir: Path,
    output_dir: Path,
    asset_stem: str,
) -> tuple[dict[str, str] | None, str | None]:
    """Copy an explicit image or official page preview into the local report."""

    source = explicit_source
    discovered = False

    if not source and product_url:
        try:
            validated_page_url = validate_web_url(product_url, "product_url")
            page_html, _, final_page_url = fetch_bytes(
                validated_page_url,
                MAX_PRODUCT_PAGE_BYTES,
                "text/html,application/xhtml+xml",
            )
            source = extract_product_image_url(page_html, final_page_url) or ""
            discovered = True
            if not source:
                return None, "No official product preview image was found on product_url."
        except InputError as exc:
            return None, str(exc)

    if not source:
        return None, None

    try:
        parsed = urlparse(source)
        remote_source_url = ""
        if parsed.scheme in {"http", "https"}:
            payload, content_type, remote_source_url = fetch_bytes(
                source,
                MAX_IMAGE_BYTES,
                "image/avif,image/webp,image/png,image/jpeg,image/gif,image/svg+xml",
            )
        elif parsed.scheme:
            raise InputError("product_image_url must be a local path or http/https URL")
        else:
            local_path = Path(source).expanduser()
            if not local_path.is_absolute():
                local_path = base_dir / local_path
            try:
                payload = local_path.read_bytes()
            except OSError as exc:
                raise InputError(
                    f"could not read product image {local_path}: {exc}"
                ) from exc
            if len(payload) > MAX_IMAGE_BYTES:
                raise InputError("local product image exceeds 8 MB")
            content_type = mimetypes.guess_type(local_path.name)[0] or ""

        extension = image_extension(payload, content_type, source)
    except InputError as exc:
        if discovered:
            return None, str(exc)
        raise

    asset_dir = output_dir / "assets"
    destination = asset_dir / f"{asset_stem}{extension}"
    try:
        asset_dir.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(payload)
    except OSError as exc:
        raise InputError(f"could not write product image {destination}: {exc}") from exc

    metadata = {
        "src": f"assets/{destination.name}",
        "alt": alt or default_alt,
        "source": str(
            source_label
            or (
                "Official product page preview"
                if discovered
                else "Provided product image"
            )
        ),
    }
    if remote_source_url:
        metadata["source_url"] = remote_source_url
    if discovered and product_url:
        metadata["product_url"] = product_url
    return metadata, None


def prepare_product_image(
    config: dict[str, Any],
    config_path: Path | None,
    output_dir: Path,
) -> tuple[dict[str, str] | None, str | None]:
    """Prepare the legacy single-product image from project configuration."""

    return prepare_image_asset(
        explicit_source=str(config.get("product_image_url") or "").strip(),
        product_url=str(config.get("product_url") or "").strip(),
        alt=str(config.get("product_image_alt") or "").strip(),
        default_alt=f"{config.get('product') or 'Product'} preview",
        source_label=str(config.get("product_image_source") or "").strip(),
        base_dir=config_path.parent if config_path is not None else Path.cwd(),
        output_dir=output_dir,
        asset_stem="product-image",
    )


def asset_slug(value: str, fallback: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug[:48] or fallback


def prepare_market_images(
    markets: list[dict[str, Any]],
    input_path: Path,
    output_dir: Path,
) -> list[str]:
    """Prepare one locally packaged image for each distinct product in the rows."""

    warnings: list[str] = []
    cache: dict[tuple[str, str, str], tuple[dict[str, str] | None, str | None]] = {}
    for index, market in enumerate(markets, start=1):
        explicit_source = str(market.get("product_image_url") or "").strip()
        product_url = str(market.get("product_url") or "").strip()
        product_name = str(market.get("product_name") or "").strip()
        if not explicit_source and not product_url:
            continue
        key = (explicit_source, product_url, product_name)
        if key not in cache:
            identifier = str(market.get("product_id") or product_name)
            cache[key] = prepare_image_asset(
                explicit_source=explicit_source,
                product_url=product_url,
                alt=str(market.get("product_image_alt") or "").strip(),
                default_alt=f"{product_name or 'Product'} preview",
                source_label=str(market.get("product_image_source") or "").strip(),
                base_dir=input_path.parent,
                output_dir=output_dir,
                asset_stem=f"product-{index}-{asset_slug(identifier, str(index))}",
            )
        metadata, warning = cache[key]
        market["product_image"] = metadata
        market["product_image_warning"] = warning or ""
        if warning:
            warnings.append(f"{product_name or market['market_name']}: {warning}")
    return warnings


def parse_number(row: dict[str, str], key: str, row_number: int) -> float:
    raw = (row.get(key) or "").strip().replace(",", "")
    try:
        value = float(raw)
    except ValueError as exc:
        raise InputError(f"row {row_number}: {key} must be numeric, got {raw!r}") from exc
    if not math.isfinite(value):
        raise InputError(f"row {row_number}: {key} must be finite")
    return value


def pct(value: float) -> float:
    return value / 100.0


def money(value: float) -> float:
    return round(value + 0.0, 2)


def formatted_money(value: float) -> str:
    sign = "-" if value < 0 else ""
    return f"{sign}${abs(value):,.2f}"


def ratio(value: float) -> float:
    return round(value + 0.0, 6)


def config_number(
    config: dict[str, Any],
    key: str,
    default: float,
    minimum: float,
    maximum: float,
) -> float:
    raw = config.get(key, default)
    try:
        value = float(raw)
    except (TypeError, ValueError) as exc:
        raise InputError(f"{key} must be numeric") from exc
    if not math.isfinite(value) or not minimum <= value <= maximum:
        raise InputError(f"{key} must be between {minimum:g} and {maximum:g}")
    return value


def periods_per_quarter(config: dict[str, Any]) -> float:
    if "periods_per_quarter" in config:
        return config_number(config, "periods_per_quarter", 3, 0.01, 1000)
    label = str(config.get("period_label") or "month").strip().lower()
    if "week" in label:
        return 13
    if "quarter" in label:
        return 1
    if "year" in label or "annual" in label:
        return 0.25
    return 3


def load_config(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise InputError(f"could not read config {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise InputError("config must be a JSON object")
    return data


def contribution_per_order(
    price_usd: float,
    tax_rate: float,
    fee_rate: float,
    fixed_fee_usd: float,
    variable_cost_usd: float,
) -> float:
    price_before_tax = price_usd / (1.0 + tax_rate)
    return (
        price_before_tax * (1.0 - fee_rate)
        - fixed_fee_usd
        - variable_cost_usd
    )


def analyze_row(row: dict[str, str], row_number: int) -> dict[str, Any]:
    for key, value in OPTIONAL_DEFAULTS.items():
        row.setdefault(key, value)

    market_id = (row.get("market_id") or "").strip().upper()
    market_name = (row.get("market_name") or "").strip()
    currency = (row.get("currency") or "").strip().upper()
    assumption_basis = (row.get("assumption_basis") or "").strip().lower()
    assumption_note = (row.get("assumption_note") or "").strip()
    product_name = (row.get("product_name") or "").strip()
    product_id = (row.get("product_id") or product_name).strip()

    if not market_id or not market_name or len(currency) != 3:
        raise InputError(
            f"row {row_number}: market_id, market_name, and a 3-letter currency are required"
        )
    if assumption_basis not in {
        "observed",
        "experiment",
        "benchmark",
        "hypothesis",
        "synthetic",
    }:
        raise InputError(
            f"row {row_number}: assumption_basis must be observed, experiment, "
            "benchmark, hypothesis, or synthetic"
        )
    if not assumption_note:
        raise InputError(f"row {row_number}: assumption_note is required")

    visitors = parse_number(row, "visitors", row_number)
    orders = parse_number(row, "orders", row_number)
    refunds = parse_number(row, "refunds", row_number)
    current_local = parse_number(row, "current_local_price", row_number)
    proposed_local = parse_number(row, "proposed_local_price", row_number)
    usd_per_local = parse_number(row, "usd_per_local", row_number)
    tax_rate = pct(parse_number(row, "tax_inclusive_pct", row_number))
    fee_rate = pct(parse_number(row, "payment_fee_pct", row_number))
    fixed_fee_usd = parse_number(row, "payment_fee_fixed_usd", row_number)
    variable_cost_usd = parse_number(row, "variable_cost_usd", row_number)
    lifts = {
        scenario: pct(parse_number(row, f"lift_{scenario}_pct", row_number))
        for scenario in SCENARIOS
    }

    if visitors <= 0:
        raise InputError(f"row {row_number}: visitors must be greater than zero")
    if orders < 0 or refunds < 0 or refunds > orders:
        raise InputError(f"row {row_number}: require orders >= refunds >= 0")
    if current_local <= 0 or proposed_local <= 0 or usd_per_local <= 0:
        raise InputError(f"row {row_number}: prices and usd_per_local must be positive")
    if not 0 <= tax_rate < 1 or not 0 <= fee_rate < 1:
        raise InputError(f"row {row_number}: tax and fee percentages must be in [0, 100)")
    if fixed_fee_usd < 0 or variable_cost_usd < 0:
        raise InputError(f"row {row_number}: fees and variable cost cannot be negative")
    if not lifts["low"] <= lifts["base"] <= lifts["high"]:
        raise InputError(f"row {row_number}: require low lift <= base lift <= high lift")
    if any(lift <= -1 for lift in lifts.values()):
        raise InputError(f"row {row_number}: lift assumptions must be greater than -100%")

    current_price_usd = current_local * usd_per_local
    proposed_price_usd = proposed_local * usd_per_local
    current_contribution_order = contribution_per_order(
        current_price_usd, tax_rate, fee_rate, fixed_fee_usd, variable_cost_usd
    )
    proposed_contribution_order = contribution_per_order(
        proposed_price_usd, tax_rate, fee_rate, fixed_fee_usd, variable_cost_usd
    )
    if current_contribution_order <= 0 or proposed_contribution_order <= 0:
        raise InputError(
            f"row {row_number}: current and proposed contribution per order must be positive"
        )

    conversion_rate = orders / visitors
    refund_rate = refunds / orders if orders else 0.0
    retained_orders = orders * (1.0 - refund_rate)
    current_contribution = retained_orders * current_contribution_order
    price_only_contribution = retained_orders * proposed_contribution_order
    price_effect = price_only_contribution - current_contribution
    break_even_lift = current_contribution_order / proposed_contribution_order - 1.0
    break_even_orders = (
        current_contribution
        / ((1.0 - refund_rate) * proposed_contribution_order)
        if orders
        else 0.0
    )
    price_change = proposed_price_usd / current_price_usd - 1.0

    scenario_results: dict[str, dict[str, float]] = {}
    for scenario, lift in lifts.items():
        projected_orders = orders * (1.0 + lift)
        projected_retained = projected_orders * (1.0 - refund_rate)
        projected_contribution = projected_retained * proposed_contribution_order
        delta = projected_contribution - current_contribution
        volume_effect = projected_contribution - price_only_contribution
        scenario_results[scenario] = {
            "lift": ratio(lift),
            "orders": ratio(projected_orders),
            "incremental_orders": ratio(projected_orders - orders),
            "retained_orders": ratio(projected_retained),
            "contribution": money(projected_contribution),
            "volume_effect": money(volume_effect),
            "delta": money(delta),
            "delta_pct": ratio(delta / current_contribution) if current_contribution else 0.0,
            "margin_of_safety": ratio(lift - break_even_lift),
            "clears_break_even": lift >= break_even_lift,
        }

    if abs(price_change) < 0.000001:
        decision = "control"
    elif lifts["high"] < break_even_lift:
        decision = "hold"
    elif lifts["low"] >= break_even_lift:
        decision = "ready for experiment"
    else:
        decision = "experiment"

    low_result = scenario_results["low"]
    base_result = scenario_results["base"]
    if decision == "control":
        recommendation_key = "control"
        recommendation_label = "Keep current price"
        recommendation_reason = "The candidate price is unchanged."
    elif not base_result["clears_break_even"]:
        recommendation_key = "needs-evidence"
        recommendation_label = "Needs more evidence"
        recommendation_reason = (
            "The base response does not recover the modeled price effect."
        )
    elif low_result["clears_break_even"]:
        recommendation_key = "strong-candidate"
        recommendation_label = "Strong test candidate"
        recommendation_reason = (
            "Even the conservative response clears the modeled break-even lift."
        )
    else:
        recommendation_key = "small-test"
        recommendation_label = "Small test only"
        recommendation_reason = (
            "The base response clears break-even, but the conservative response loses contribution."
        )

    conservative_downside = abs(min(0.0, low_result["delta"]))
    base_upside = max(0.0, base_result["delta"])
    return {
        "product_id": product_id,
        "product_name": product_name,
        "product_url": (row.get("product_url") or "").strip(),
        "product_image_url": (row.get("product_image_url") or "").strip(),
        "product_image_alt": (row.get("product_image_alt") or "").strip(),
        "product_image_source": (row.get("product_image_source") or "").strip(),
        "product_image": None,
        "product_image_warning": "",
        "market_id": market_id,
        "market_name": market_name,
        "currency": currency,
        "visitors": round(visitors),
        "orders": round(orders),
        "refunds": round(refunds),
        "conversion_rate": ratio(conversion_rate),
        "refund_rate": ratio(refund_rate),
        "current_local_price": money(current_local),
        "proposed_local_price": money(proposed_local),
        "usd_per_local": ratio(usd_per_local),
        "current_price_usd": money(current_price_usd),
        "proposed_price_usd": money(proposed_price_usd),
        "price_change_pct": ratio(price_change),
        "tax_inclusive_pct": ratio(tax_rate),
        "payment_fee_pct": ratio(fee_rate),
        "payment_fee_fixed_usd": money(fixed_fee_usd),
        "variable_cost_usd": money(variable_cost_usd),
        "current_contribution_per_order": money(current_contribution_order),
        "proposed_contribution_per_order": money(proposed_contribution_order),
        "current_contribution": money(current_contribution),
        "price_only_contribution": money(price_only_contribution),
        "price_effect": money(price_effect),
        "break_even_lift": ratio(break_even_lift),
        "break_even_orders": ratio(break_even_orders),
        "incremental_orders_to_break_even": ratio(break_even_orders - orders),
        "assumption_basis": assumption_basis,
        "assumption_note": assumption_note,
        "decision": decision,
        "recommendation_key": recommendation_key,
        "recommendation_label": recommendation_label,
        "recommendation_reason": recommendation_reason,
        "conservative_downside": money(conservative_downside),
        "base_upside": money(base_upside),
        "downside_to_base_ratio": (
            ratio(conservative_downside / base_upside)
            if conservative_downside and base_upside
            else None
        ),
        "scenarios": scenario_results,
    }


def load_markets(path: Path) -> list[dict[str, Any]]:
    try:
        with path.open(newline="", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle)
            columns = set(reader.fieldnames or [])
            missing = sorted(REQUIRED_COLUMNS - columns)
            if missing:
                raise InputError(f"input CSV is missing columns: {', '.join(missing)}")
            markets = [
                analyze_row(dict(row), index)
                for index, row in enumerate(reader, start=2)
            ]
    except OSError as exc:
        raise InputError(f"could not read input CSV {path}: {exc}") from exc
    if not markets:
        raise InputError("input CSV contains no market rows")
    return markets


def build_report(config: dict[str, Any], markets: list[dict[str, Any]]) -> dict[str, Any]:
    default_product = str(config.get("product") or "Digital product")
    legacy_image = (
        config.get("product_image")
        if isinstance(config.get("product_image"), dict)
        else None
    )
    for market in markets:
        if not market.get("product_name"):
            market["product_name"] = default_product
        if not market.get("product_id"):
            market["product_id"] = market["product_name"]
        if not market.get("product_image") and legacy_image:
            market["product_image"] = legacy_image

    scenario_totals = {
        scenario: money(sum(market["scenarios"][scenario]["contribution"] for market in markets))
        for scenario in SCENARIOS
    }
    current_total = money(sum(market["current_contribution"] for market in markets))
    for scenario in SCENARIOS:
        scenario_totals[f"{scenario}_delta"] = money(scenario_totals[scenario] - current_total)
        scenario_totals[f"{scenario}_delta_pct"] = (
            ratio((scenario_totals[scenario] - current_total) / current_total)
            if current_total
            else 0.0
        )

    report_config = {
        "project": str(config.get("project") or "Regional pricing analysis"),
        "product": default_product,
        "analysis_date": str(config.get("analysis_date") or date.today().isoformat()),
        "period_label": str(config.get("period_label") or "analysis period"),
        "base_currency": str(config.get("base_currency") or "USD").upper(),
        "cohort": str(config.get("cohort") or "Eligible new customers"),
        "data_label": str(config.get("data_label") or "Planning assumptions"),
        "revenue_basis": str(
            config.get("revenue_basis") or "First-order contribution revenue"
        ),
        "sources": config.get("sources") if isinstance(config.get("sources"), list) else [],
        "product_image": legacy_image,
        "product_image_warning": str(config.get("product_image_warning") or ""),
        "product_image_warnings": (
            config.get("product_image_warnings")
            if isinstance(config.get("product_image_warnings"), list)
            else []
        ),
        "periods_per_quarter": periods_per_quarter(config),
        "default_test_reach_pct": config_number(
            config, "default_test_reach_pct", 10, 5, 100
        ),
        "default_horizon_quarters": round(
            config_number(config, "default_horizon_quarters", 4, 1, 4)
        ),
    }

    price_only_total = money(
        sum(market["price_only_contribution"] for market in markets)
    )
    return {
        "schema_version": 2,
        "generated_at": date.today().isoformat(),
        "local_only": True,
        "config": report_config,
        "summary": {
            "visitors": round(sum(market["visitors"] for market in markets)),
            "orders": round(sum(market["orders"] for market in markets)),
            "current_contribution": current_total,
            "price_only_contribution": price_only_total,
            "price_effect": money(price_only_total - current_total),
            **scenario_totals,
            "base_markets_clearing_break_even": sum(
                bool(
                    market["decision"] != "control"
                    and market["scenarios"]["base"]["clears_break_even"]
                )
                for market in markets
            ),
            "candidate_market_count": sum(
                market["decision"] != "control" for market in markets
            ),
            "product_count": len(
                {
                    market["product_id"]
                    for market in markets
                    if market["decision"] != "control"
                }
            ),
            "market_count": len(markets),
            "strong_candidate_count": sum(
                market["recommendation_key"] == "strong-candidate"
                for market in markets
            ),
            "small_test_count": sum(
                market["recommendation_key"] == "small-test"
                for market in markets
            ),
            "needs_evidence_count": sum(
                market["recommendation_key"] == "needs-evidence"
                for market in markets
            ),
        },
        "markets": markets,
        "disclaimer": (
            "Scenario output depends on supplied conversion-lift assumptions. "
            "It is not a guarantee or a live pricing change."
        ),
    }


def write_json(path: Path, report: dict[str, Any]) -> None:
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


def write_csv(path: Path, markets: list[dict[str, Any]]) -> None:
    fields = [
        "product_id",
        "product_name",
        "product_image_src",
        "market_id",
        "market_name",
        "currency",
        "current_local_price",
        "proposed_local_price",
        "current_price_usd",
        "proposed_price_usd",
        "price_change_pct",
        "conversion_rate",
        "refund_rate",
        "break_even_lift",
        "lift_low",
        "lift_base",
        "lift_high",
        "current_contribution",
        "price_only_contribution",
        "price_effect",
        "low_contribution",
        "base_contribution",
        "high_contribution",
        "base_volume_effect",
        "incremental_orders_to_break_even",
        "base_delta",
        "decision",
        "recommendation_key",
        "recommendation_label",
        "recommendation_reason",
        "conservative_downside",
        "downside_to_base_ratio",
        "assumption_basis",
        "assumption_note",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for market in markets:
            writer.writerow(
                {
                    "product_id": market["product_id"],
                    "product_name": market["product_name"],
                    "product_image_src": (
                        market["product_image"]["src"]
                        if market.get("product_image")
                        else ""
                    ),
                    "market_id": market["market_id"],
                    "market_name": market["market_name"],
                    "currency": market["currency"],
                    "current_local_price": market["current_local_price"],
                    "proposed_local_price": market["proposed_local_price"],
                    "current_price_usd": market["current_price_usd"],
                    "proposed_price_usd": market["proposed_price_usd"],
                    "price_change_pct": market["price_change_pct"],
                    "conversion_rate": market["conversion_rate"],
                    "refund_rate": market["refund_rate"],
                    "break_even_lift": market["break_even_lift"],
                    "lift_low": market["scenarios"]["low"]["lift"],
                    "lift_base": market["scenarios"]["base"]["lift"],
                    "lift_high": market["scenarios"]["high"]["lift"],
                    "current_contribution": market["current_contribution"],
                    "price_only_contribution": market["price_only_contribution"],
                    "price_effect": market["price_effect"],
                    "low_contribution": market["scenarios"]["low"]["contribution"],
                    "base_contribution": market["scenarios"]["base"]["contribution"],
                    "high_contribution": market["scenarios"]["high"]["contribution"],
                    "base_volume_effect": market["scenarios"]["base"]["volume_effect"],
                    "incremental_orders_to_break_even": market[
                        "incremental_orders_to_break_even"
                    ],
                    "base_delta": market["scenarios"]["base"]["delta"],
                    "decision": market["decision"],
                    "recommendation_key": market["recommendation_key"],
                    "recommendation_label": market["recommendation_label"],
                    "recommendation_reason": market["recommendation_reason"],
                    "conservative_downside": market["conservative_downside"],
                    "downside_to_base_ratio": market["downside_to_base_ratio"],
                    "assumption_basis": market["assumption_basis"],
                    "assumption_note": market["assumption_note"],
                }
            )


def write_summary(path: Path, report: dict[str, Any]) -> None:
    config = report["config"]
    summary = report["summary"]
    lines = [
        f"# {config['project']}",
        "",
        f"**Scope:** {config['product']}  ",
        f"**Cohort:** {config['cohort']}  ",
        f"**Data:** {config['data_label']}  ",
        f"**Revenue basis:** {config['revenue_basis']}  ",
        f"**Analysis date:** {config['analysis_date']}",
        "",
        "## Scenario summary",
        "",
        f"- Current contribution revenue: ${summary['current_contribution']:,.2f}",
        (
            "- Price effect at unchanged order volume: "
            f"{formatted_money(summary['price_effect'])}"
        ),
        f"- Low scenario: ${summary['low']:,.2f} ({summary['low_delta_pct']:+.1%})",
        f"- Base scenario: ${summary['base']:,.2f} ({summary['base_delta_pct']:+.1%})",
        f"- High scenario: ${summary['high']:,.2f} ({summary['high_delta_pct']:+.1%})",
        (
            "- Product-market changes clearing break-even in the base scenario: "
            f"{summary['base_markets_clearing_break_even']} of "
            f"{summary['candidate_market_count']} candidates"
        ),
        "",
        "## Product and market decisions",
        "",
        "| Product | Market | Price change | Break-even lift | Base lift | Recommendation |",
        "| --- | --- | ---: | ---: | ---: | --- |",
    ]
    for market in report["markets"]:
        lines.append(
            f"| {market['product_name']} | {market['market_name']} | "
            f"{market['price_change_pct']:+.1%} | "
            f"{market['break_even_lift']:+.1%} | "
            f"{market['scenarios']['base']['lift']:+.1%} | "
            f"{market['recommendation_label']} |"
        )
    lines.extend(
        [
            "",
            "## Guardrail",
            "",
            report["disclaimer"],
            "No live prices or production systems were changed.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def write_html(template_path: Path, output_path: Path, report: dict[str, Any]) -> None:
    try:
        template = template_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise InputError(f"could not read report template {template_path}: {exc}") from exc
    json_payload = json.dumps(report, separators=(",", ":")).replace("</", "<\\/")
    title = html.escape(f"{report['config']['project']} — Regional pricing")
    rendered = template.replace("__REPORT_TITLE__", title).replace(
        "__REPORT_DATA__", json_payload
    )
    if "__REPORT_DATA__" in rendered or "__REPORT_TITLE__" in rendered:
        raise InputError("report template placeholders were not fully replaced")
    output_path.write_text(rendered, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a local regional-pricing scenario report."
    )
    parser.add_argument("--input", required=True, type=Path, help="Market CSV")
    parser.add_argument("--config", type=Path, help="Project JSON")
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--template", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    skill_dir = Path(__file__).resolve().parent.parent
    template = args.template or skill_dir / "assets" / "regional-pricing-report.html"
    try:
        config = load_config(args.config)
        markets = load_markets(args.input)
        args.output_dir.mkdir(parents=True, exist_ok=True)
        product_image, product_image_warning = prepare_product_image(
            config, args.config, args.output_dir
        )
        config = dict(config)
        if product_image:
            config["product_image"] = product_image
        if product_image_warning:
            config["product_image_warning"] = product_image_warning
        product_image_warnings = prepare_market_images(
            markets, args.input, args.output_dir
        )
        if product_image_warnings:
            config["product_image_warnings"] = product_image_warnings
        report = build_report(config, markets)
        write_json(args.output_dir / "regional-pricing-analysis.json", report)
        write_csv(args.output_dir / "regional-pricing-analysis.csv", markets)
        write_summary(args.output_dir / "regional-pricing-summary.md", report)
        write_html(template, args.output_dir / "index.html", report)
    except InputError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print(f"REPORT_HTML={args.output_dir / 'index.html'}")
    print(f"REPORT_JSON={args.output_dir / 'regional-pricing-analysis.json'}")
    if report["config"]["product_image"]:
        print(
            "PRODUCT_IMAGE="
            f"{args.output_dir / report['config']['product_image']['src']}"
        )
    elif report["config"]["product_image_warning"]:
        print(f"PRODUCT_IMAGE_WARNING={report['config']['product_image_warning']}")
    else:
        print("PRODUCT_IMAGE=none")
    packaged_row_images = sum(bool(market.get("product_image")) for market in markets)
    print(f"PRODUCT_ROW_IMAGES={packaged_row_images}")
    print("LIVE_CHANGES=none")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
