#!/usr/bin/env python3
"""Normalize a saved Fluid product response and enrich pricing-analysis rows.

This script intentionally performs no network requests and has no write path to
Fluid. An agent or approved read-only connector supplies the saved catalog JSON.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any, Iterable


class CatalogError(ValueError):
    pass


def first_text(*values: Any) -> str:
    for value in values:
        if value is not None and str(value).strip():
            return str(value).strip()
    return ""


def product_records(payload: Any) -> list[dict[str, Any]]:
    """Accept the documented list/detail response and common MCP wrappers."""

    candidates: list[Any] = [payload]
    if isinstance(payload, dict):
        candidates.extend(
            value
            for key in ("data", "result", "response")
            if isinstance((value := payload.get(key)), (dict, list))
        )

    for candidate in candidates:
        if isinstance(candidate, list):
            products = candidate
        elif isinstance(candidate, dict):
            products = candidate.get("products")
            if products is None and isinstance(candidate.get("product"), dict):
                products = [candidate["product"]]
        else:
            continue
        if isinstance(products, list) and all(
            isinstance(product, dict) for product in products
        ):
            return products

    raise CatalogError(
        "catalog JSON must contain products[] or product, optionally under data/result"
    )


def image_candidates(record: dict[str, Any]) -> Iterable[str]:
    for key in ("compressed_image_url", "image_url", "primary_image"):
        value = record.get(key)
        if isinstance(value, str) and value.strip():
            yield value.strip()

    images = record.get("images")
    if isinstance(images, list):
        ranked: list[tuple[int, str]] = []
        for index, image in enumerate(images):
            if isinstance(image, str):
                ranked.append((index, image))
                continue
            if not isinstance(image, dict):
                continue
            url = first_text(image.get("image_url"), image.get("url"), image.get("src"))
            if not url:
                continue
            try:
                position = int(image.get("position", index))
            except (TypeError, ValueError):
                position = index
            ranked.append((position, url))
        for _, url in sorted(ranked):
            yield url


def choose_product_image(
    product: dict[str, Any], variants: list[dict[str, Any]]
) -> str:
    for candidate in image_candidates(product):
        return candidate
    for variant in variants:
        for candidate in image_candidates(variant):
            return candidate
    return ""


def country_records(value: Any) -> Iterable[dict[str, Any]]:
    if isinstance(value, list):
        for item in value:
            if isinstance(item, dict):
                yield item
    elif isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(item, dict):
                continue
            copied = dict(item)
            copied.setdefault("_map_key", key)
            yield copied


def normalize_market_price(
    country: dict[str, Any], *, variant_id: str
) -> dict[str, Any] | None:
    nested_country = country.get("country")
    if not isinstance(nested_country, dict):
        nested_country = {}
    market_id = first_text(
        country.get("country_iso"),
        country.get("country_code"),
        nested_country.get("iso"),
        country.get("_map_key"),
    ).upper()
    raw_price = country.get("price")
    if not market_id or raw_price is None or str(raw_price).strip() == "":
        return None
    try:
        price = float(raw_price)
    except (TypeError, ValueError):
        return None
    return {
        "market_id": market_id,
        "market_name": first_text(
            country.get("country_name"), nested_country.get("name")
        ),
        "currency": first_text(country.get("currency_code")).upper(),
        "price": price,
        "display_price": first_text(country.get("display_price")),
        "active": country.get("active"),
        "variant_id": variant_id,
    }


def normalize_variant(variant: dict[str, Any]) -> dict[str, Any]:
    variant_id = first_text(variant.get("id"))
    prices = [
        price
        for country in country_records(variant.get("variant_countries"))
        if (price := normalize_market_price(country, variant_id=variant_id))
    ]
    return {
        "variant_id": variant_id,
        "title": first_text(variant.get("title"), variant.get("display_name")),
        "sku": first_text(variant.get("sku")),
        "is_master": bool(variant.get("is_master")),
        "image_url": next(iter(image_candidates(variant)), ""),
        "market_prices": prices,
    }


def normalize_product(product: dict[str, Any]) -> dict[str, Any]:
    variants_source = product.get("variants")
    if not isinstance(variants_source, list):
        variants_source = []
    variants = [
        variant for variant in variants_source if isinstance(variant, dict)
    ]
    normalized_variants = [normalize_variant(variant) for variant in variants]

    fallback_prices: list[dict[str, Any]] = []
    if product.get("price") is not None:
        try:
            fallback_price = float(product["price"])
        except (TypeError, ValueError):
            fallback_price = None
        if fallback_price is not None:
            fallback_prices.append(
                {
                    "market_id": "",
                    "market_name": "",
                    "currency": first_text(product.get("currency_code")).upper(),
                    "price": fallback_price,
                    "display_price": first_text(product.get("display_price")),
                    "active": product.get("active"),
                    "variant_id": "",
                }
            )

    return {
        "product_id": first_text(product.get("id")),
        "product_name": first_text(product.get("title"), "Untitled product"),
        "product_url": first_text(
            product.get("canonical_url"), product.get("external_url")
        ),
        "product_image_url": choose_product_image(product, variants),
        "status": first_text(product.get("status")),
        "variants": normalized_variants,
        "fallback_prices": fallback_prices,
    }


def normalize_catalog(payload: Any, source_path: Path) -> dict[str, Any]:
    products = [normalize_product(product) for product in product_records(payload)]
    products_with_images = sum(bool(product["product_image_url"]) for product in products)
    products_with_market_prices = sum(
        any(variant["market_prices"] for variant in product["variants"])
        for product in products
    )
    return {
        "schema_version": 1,
        "source": "Saved Fluid Products API response",
        "source_file": str(source_path.resolve()),
        "read_only": True,
        "products": products,
        "summary": {
            "product_count": len(products),
            "products_with_images": products_with_images,
            "products_with_market_prices": products_with_market_prices,
        },
    }


def select_variant(
    product: dict[str, Any], requested_variant_id: str
) -> dict[str, Any] | None:
    variants = product["variants"]
    if requested_variant_id:
        return next(
            (
                variant
                for variant in variants
                if variant["variant_id"] == requested_variant_id
            ),
            None,
        )
    return next(
        (variant for variant in variants if variant["is_master"]),
        variants[0] if variants else None,
    )


def select_market_price(
    product: dict[str, Any],
    variant: dict[str, Any] | None,
    market_id: str,
) -> dict[str, Any] | None:
    market_id = market_id.upper()
    candidates: list[dict[str, Any]] = []
    if variant:
        candidates.extend(variant["market_prices"])
    for candidate_variant in product["variants"]:
        if candidate_variant is not variant:
            candidates.extend(candidate_variant["market_prices"])
    return next(
        (
            price
            for price in candidates
            if price["market_id"].upper() == market_id
        ),
        None,
    )


def enrich_market_rows(
    catalog: dict[str, Any], rows: list[dict[str, str]]
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    products = {
        product["product_id"]: product
        for product in catalog["products"]
        if product["product_id"]
    }
    unresolved: list[dict[str, str]] = []
    enriched_rows: list[dict[str, str]] = []

    for row_number, source_row in enumerate(rows, start=2):
        row = dict(source_row)
        product_id = first_text(row.get("product_id"))
        market_id = first_text(row.get("market_id")).upper()
        product = products.get(product_id)
        if not product:
            unresolved.append(
                {
                    "row": str(row_number),
                    "product_id": product_id,
                    "market_id": market_id,
                    "reason": "product not found in Fluid catalog snapshot",
                }
            )
            enriched_rows.append(row)
            continue

        row["product_name"] = product["product_name"]
        row["product_url"] = product["product_url"]
        row["product_image_url"] = product["product_image_url"]
        row["product_image_alt"] = f"{product['product_name']} product image"
        row["product_image_source"] = "Fluid product catalog snapshot"

        variant = select_variant(product, first_text(row.get("variant_id")))
        price = select_market_price(product, variant, market_id)
        if price:
            row["current_local_price"] = str(price["price"])
            if price["currency"]:
                row["currency"] = price["currency"]
        else:
            unresolved.append(
                {
                    "row": str(row_number),
                    "product_id": product_id,
                    "market_id": market_id,
                    "reason": "country-specific price not present in saved response",
                }
            )
        enriched_rows.append(row)

    audit = {
        "read_only": True,
        "input_row_count": len(rows),
        "enriched_row_count": len(rows) - sum(
            item["reason"].startswith("product not found") for item in unresolved
        ),
        "unresolved": unresolved,
    }
    return enriched_rows, audit


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CatalogError(f"could not read catalog JSON {path}: {exc}") from exc


def load_csv(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    try:
        with path.open(newline="", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle)
            if not reader.fieldnames:
                raise CatalogError(f"market CSV {path} has no header")
            return list(reader), list(reader.fieldnames)
    except OSError as exc:
        raise CatalogError(f"could not read market CSV {path}: {exc}") from exc


def write_csv(path: Path, rows: list[dict[str, str]], source_fields: list[str]) -> None:
    extra_fields = [
        "product_name",
        "product_url",
        "product_image_url",
        "product_image_alt",
        "product_image_source",
    ]
    fieldnames = source_fields + [
        field for field in extra_fields if field not in source_fields
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Normalize a saved Fluid product response and optionally enrich "
            "regional-pricing rows. Makes no network or Fluid write requests."
        )
    )
    parser.add_argument("--catalog", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--market-input", type=Path)
    parser.add_argument("--market-output", type=Path)
    args = parser.parse_args(argv)
    if bool(args.market_input) != bool(args.market_output):
        parser.error("--market-input and --market-output must be supplied together")
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        catalog = normalize_catalog(load_json(args.catalog), args.catalog)
        if args.market_input:
            rows, fields = load_csv(args.market_input)
            enriched_rows, audit = enrich_market_rows(catalog, rows)
            write_csv(args.market_output, enriched_rows, fields)
            catalog["enrichment"] = audit
            catalog["enrichment"]["source_market_file"] = str(
                args.market_input.resolve()
            )
            catalog["enrichment"]["output_market_file"] = str(
                args.market_output.resolve()
            )
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(catalog, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    except (CatalogError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
