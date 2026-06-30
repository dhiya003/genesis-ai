"""Deterministic binary asset generation for Sprint 4 Creative Studio."""

from __future__ import annotations

import re
import struct
import zlib
from pathlib import Path
from typing import Any


def generate_creative_assets(output_dir: Path, creative_pack: dict[str, Any]) -> dict[str, Any]:
    """Write no-credential creative assets and return their manifest."""
    output_dir.mkdir(parents=True, exist_ok=True)
    brand = creative_pack["brandIdentity"]["brandName"]
    product = creative_pack.get("sourceIdea", creative_pack["productId"])
    colors = _palette(creative_pack)
    assets: list[dict[str, Any]] = []

    logo_specs = [
        ("logo-primary-horizontal.svg", "Primary Horizontal Logo", 720, 240, "horizontal"),
        ("logo-stacked.svg", "Stacked Logo", 420, 420, "stacked"),
        ("logo-icon-mark.svg", "Icon Mark", 320, 320, "icon"),
        ("logo-monochrome.svg", "Monochrome Logo", 720, 240, "mono"),
    ]
    for file_name, title, width, height, variant in logo_specs:
        path = output_dir / file_name
        _write_text(path, _logo_svg(brand, title, width, height, variant, colors))
        assets.append(_asset_record("logo", title, "image/svg+xml", path, "GENERATED"))

    image_specs = [
        ("product-hero.png", "Product Hero Image", 640, 360),
        ("product-mockup-starter.png", "Starter Variant Mockup", 512, 512),
        ("amazon-main-image.png", "Amazon Main Image", 800, 800),
        ("shopify-product-card.png", "Shopify Product Card", 640, 640),
        ("instagram-launch-post.png", "Instagram Launch Post", 512, 512),
        ("instagram-story.png", "Instagram Story", 512, 896),
        ("email-launch-header.png", "Email Launch Header", 640, 260),
    ]
    for index, (file_name, title, width, height) in enumerate(image_specs):
        path = output_dir / file_name
        _write_png(path, width, height, colors, index)
        assets.append(_asset_record("raster", title, "image/png", path, "GENERATED"))

    packaging_files = [
        ("starter-box-dieline.svg", "Starter Box Dieline", "image/svg+xml", _dieline_svg(brand, colors)),
        ("packaging-spec.pdf", "Packaging Specification PDF", "application/pdf", _simple_pdf([brand, "Packaging Specification", "Panels: front, back, top, bottom, left, right", "Final printer template required before mass production."])),
        ("parent-guide.pdf", "Parent Guide PDF", "application/pdf", _simple_pdf([brand, "Parent Guide", "How to play", "Safety notes", "Care instructions"])),
        ("instruction-cards.pdf", "Instruction Cards PDF", "application/pdf", _simple_pdf([brand, "Instruction Cards", "Pattern", "Sort", "Sequence", "Match"])),
    ]
    for file_name, title, content_type, payload in packaging_files:
        path = output_dir / file_name
        if isinstance(payload, bytes):
            path.write_bytes(payload)
        else:
            _write_text(path, payload)
        assets.append(_asset_record("document", title, content_type, path, "GENERATED"))

    return {
        "assetRoot": str(output_dir),
        "provider": "deterministic-local",
        "mode": "NO_CREDENTIALS",
        "summary": {
            "totalAssets": len(assets),
            "svg": len([asset for asset in assets if asset["format"] == "svg"]),
            "png": len([asset for asset in assets if asset["format"] == "png"]),
            "pdf": len([asset for asset in assets if asset["format"] == "pdf"]),
        },
        "assets": assets,
        "notes": [
            "Assets are generated without external providers for deterministic CI.",
            "PNG files are layout placeholders; premium lifestyle imagery still benefits from an image provider.",
            f"Source product context: {product}",
        ],
    }


def _asset_record(kind: str, name: str, content_type: str, path: Path, status: str) -> dict[str, Any]:
    return {
        "assetId": _slug(name),
        "kind": kind,
        "name": name,
        "fileName": path.name,
        "format": path.suffix.removeprefix("."),
        "contentType": content_type,
        "path": str(path),
        "sizeBytes": path.stat().st_size,
        "status": status,
    }


def _palette(creative_pack: dict[str, Any]) -> list[str]:
    colors = [str(item.get("hex", "")).strip() for item in creative_pack.get("colorPalette", []) if isinstance(item, dict)]
    valid = [color for color in colors if re.fullmatch(r"#[0-9A-Fa-f]{6}", color)]
    fallback = ["#1F6F50", "#F4B63F", "#FFF7E6", "#2F2F2F"]
    return (valid + fallback)[:4]


def _logo_svg(brand: str, title: str, width: int, height: int, variant: str, colors: list[str]) -> str:
    primary, accent, background, ink = colors[0], colors[1], colors[2], colors[-1]
    if variant == "mono":
        primary = ink = "#222222"
        accent = "#F7F7F7"
        background = "#FFFFFF"
    brand_text = _escape_xml(brand)
    subtitle = _escape_xml(title)
    if variant == "icon":
        text = ""
    elif variant == "stacked":
        text = f'<text x="{width / 2}" y="{height - 82}" text-anchor="middle" font-size="34" font-family="Arial" font-weight="700" fill="{ink}">{brand_text}</text>'
    else:
        text = f'<text x="220" y="124" font-size="42" font-family="Arial" font-weight="700" fill="{ink}">{brand_text}</text><text x="222" y="164" font-size="18" font-family="Arial" fill="{primary}">{subtitle}</text>'
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <rect width="100%" height="100%" rx="18" fill="{background}"/>
  <rect x="36" y="36" width="{height - 72}" height="{height - 72}" rx="28" fill="{primary}"/>
  <circle cx="{height / 2}" cy="{height / 2}" r="{max(28, height / 7)}" fill="{accent}"/>
  <path d="M {height / 2 - 36} {height / 2} L {height / 2 - 4} {height / 2 + 32} L {height / 2 + 48} {height / 2 - 38}" fill="none" stroke="{background}" stroke-width="16" stroke-linecap="round" stroke-linejoin="round"/>
  {text}
</svg>
"""


def _dieline_svg(brand: str, colors: list[str]) -> str:
    primary, accent, background, ink = colors[0], colors[1], colors[2], colors[-1]
    brand_text = _escape_xml(brand)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="820" viewBox="0 0 1200 820">
  <rect width="100%" height="100%" fill="{background}"/>
  <g fill="none" stroke="{primary}" stroke-width="4">
    <rect x="360" y="230" width="320" height="220"/>
    <rect x="360" y="40" width="320" height="190"/>
    <rect x="360" y="450" width="320" height="190"/>
    <rect x="120" y="230" width="240" height="220"/>
    <rect x="680" y="230" width="240" height="220"/>
    <rect x="920" y="230" width="160" height="220"/>
  </g>
  <g stroke="{accent}" stroke-width="3" stroke-dasharray="14 10">
    <line x1="360" y1="230" x2="680" y2="450"/>
    <line x1="680" y1="230" x2="360" y2="450"/>
  </g>
  <text x="520" y="340" text-anchor="middle" font-family="Arial" font-size="36" font-weight="700" fill="{ink}">{brand_text}</text>
  <text x="520" y="388" text-anchor="middle" font-family="Arial" font-size="20" fill="{primary}">Starter Box Dieline - deterministic draft</text>
</svg>
"""


def _write_png(path: Path, width: int, height: int, colors: list[str], seed: int) -> None:
    rgb = [_hex_to_rgb(color) for color in colors]
    rows = []
    for y in range(height):
        row = bytearray([0])
        for x in range(width):
            band = ((x * 3 // max(width, 1)) + (y * 3 // max(height, 1)) + seed) % len(rgb)
            base = rgb[band]
            if (x - width // 2) ** 2 + (y - height // 2) ** 2 < (min(width, height) // 5) ** 2:
                base = rgb[(band + 1) % len(rgb)]
            row.extend(base)
        rows.append(bytes(row))
    raw = b"".join(rows)
    payload = b"\x89PNG\r\n\x1a\n"
    payload += _png_chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
    payload += _png_chunk(b"IDAT", zlib.compress(raw, 9))
    payload += _png_chunk(b"IEND", b"")
    path.write_bytes(payload)


def _png_chunk(kind: bytes, data: bytes) -> bytes:
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)


def _simple_pdf(lines: list[str]) -> bytes:
    escaped = [_escape_pdf(line[:92]) for line in lines]
    text_ops = ["BT", "/F1 18 Tf", "72 760 Td"]
    for index, line in enumerate(escaped):
        if index:
            text_ops.append("0 -32 Td")
        text_ops.append(f"({line}) Tj")
    text_ops.append("ET")
    stream = "\n".join(text_ops).encode("ascii")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"\nendstream",
    ]
    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for number, obj in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf.extend(f"{number} 0 obj\n".encode("ascii"))
        pdf.extend(obj)
        pdf.extend(b"\nendobj\n")
    xref = len(pdf)
    pdf.extend(f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode("ascii"))
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    pdf.extend(f"trailer << /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode("ascii"))
    return bytes(pdf)


def _hex_to_rgb(color: str) -> bytes:
    value = color.lstrip("#")
    return bytes(int(value[index : index + 2], 16) for index in (0, 2, 4))


def _write_text(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _escape_xml(value: str) -> str:
    return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _escape_pdf(value: str) -> str:
    return value.encode("ascii", "ignore").decode("ascii").replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
