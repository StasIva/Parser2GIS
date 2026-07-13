#!/usr/bin/env python3
"""Generate application icon files (PNG, ICO) from the SVG source."""

from __future__ import annotations

import io
import os
import struct
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
SVG_PATH = PROJECT_ROOT / "parser2gis" / "assets" / "icon.svg"
OUTPUT_DIR = PROJECT_ROOT / "parser2gis" / "assets"
ICO_SIZES = [16, 32, 48, 64, 128, 256]


def _check_rsvg() -> bool:
    try:
        subprocess.run(["rsvg-convert", "--version"], capture_output=True, check=True)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


def _svg_to_png_rsvg(svg_path: Path, size: int) -> bytes:
    result = subprocess.run(
        ["rsvg-convert", "-w", str(size), "-h", str(size), "-f", "png", "-o", "/dev/stdout", str(svg_path)],
        capture_output=True, check=True,
    )
    return result.stdout


def _svg_to_png_fallback(svg_path: Path, size: int) -> bytes | None:
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        return None

    tree = ET.parse(svg_path)
    root = tree.getroot()
    view_box = root.get("viewBox", "0 0 64 64")
    parts = view_box.split()
    vb_w = float(parts[2]) if len(parts) > 2 else 64
    vb_h = float(parts[3]) if len(parts) > 3 else 64

    scale = size / max(vb_w, vb_h)
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))

    draw = ImageDraw.Draw(img)
    center_x, center_y = size / 2, size / 2
    r = size * 0.45

    draw.ellipse(
        [center_x - r, center_y - r, center_x + r, center_y + r],
        fill=(37, 99, 235, 242),
    )
    draw.ellipse(
        [center_x - r * 0.35, center_y - r * 0.35, center_x + r * 0.35, center_y + r * 0.35],
        fill=(255, 255, 255, 255),
    )

    img_bytes = io.BytesIO()
    img.save(img_bytes, format="PNG")
    return img_bytes.getvalue()


def _make_ico(png_sizes: dict[int, bytes]) -> bytes:
    """Create ICO from PNG data for each size."""
    header_size = 6
    entry_size = 16
    num_sizes = len(png_sizes)
    offset = header_size + num_sizes * entry_size

    buf = io.BytesIO()
    buf.write(struct.pack("<HHH", 0, 1, num_sizes))

    data_blocks: list[bytes] = []
    for size in sorted(png_sizes.keys()):
        png_data = png_sizes[size]
        data_blocks.append(png_data)

    data_offset = offset
    for size in sorted(png_sizes.keys()):
        png_data = png_sizes[size]
        real_w = size if size < 256 else 0
        real_h = size if size < 256 else 0
        bpp = 32
        buf.write(struct.pack("<BBBBHHII", real_w, real_h, 0, 0, 1, bpp, data_offset, len(png_data)))
        data_offset += len(png_data)

    for png_data in data_blocks:
        buf.write(png_data)

    return buf.getvalue()


def main() -> None:
    print("[icons] Generating application icons...")

    use_rsvg = _check_rsvg()
    if use_rsvg:
        print("[icons] Using rsvg-convert for SVG rasterization")
    else:
        print("[icons] rsvg-convert not found, using Pillow fallback")

    png_sizes: dict[int, bytes] = {}

    for size in ICO_SIZES:
        if use_rsvg:
            png_data = _svg_to_png_rsvg(SVG_PATH, size)
        else:
            png_data = _svg_to_png_fallback(SVG_PATH, size)
            if png_data is None:
                print("[icons] Pillow not available either, skipping PNG generation", file=sys.stderr)
                break

        if png_data:
            out_path = OUTPUT_DIR / f"icon-{size}.png"
            out_path.write_bytes(png_data)
            print(f"[icons]  Created {out_path.name} ({len(png_data)} bytes)")
            png_sizes[size] = png_data

    if png_sizes:
        ico_data = _make_ico(png_sizes)
        ico_path = OUTPUT_DIR / "icon.ico"
        ico_path.write_bytes(ico_data)
        print(f"[icons]  Created {ico_path.name} ({len(ico_data)} bytes)")

        png_256 = png_sizes.get(256)
        if png_256:
            icon_png_path = PROJECT_ROOT / "parser2gis" / "assets" / "icon.png"
            icon_png_path.write_bytes(png_256)
            print(f"[icons]  Created {icon_png_path.name} ({len(png_256)} bytes)")

    print("[icons] Done.")


if __name__ == "__main__":
    main()
