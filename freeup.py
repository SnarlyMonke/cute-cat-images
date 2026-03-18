"""Rename images in 'raw images' folder to sequential 10-digit numbers.

Converts all PNG and JPG files in the 'raw images' folder to PNG format and renames
them to 10-digit zero-padded numbers (e.g., 0000000000.png, 0000000001.png, ...).
Skips files that are already named with 10 digits.

Usage:
    python freeup.py

If Pillow is installed (PIL), images will be converted to PNG. If it's not installed,
the script will just rename files to .png extension (keeping original format).
"""

from __future__ import annotations

import re
from pathlib import Path

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    Image = None  # type: ignore


def main() -> int:
    root = Path(__file__).resolve().parent
    raw_dir = root / "raw images"

    if not raw_dir.exists():
        print(f"ERROR: input directory does not exist: {raw_dir}")
        return 1

    # Collect image files (case-insensitive extension match).
    image_paths = [
        p for p in raw_dir.iterdir()
        if p.is_file() and p.suffix.lower() in {".png", ".jpg", ".jpeg"}
    ]

    if not image_paths:
        print(f"No PNG/JPG images found in {raw_dir}.")
        return 0

    # Find the highest existing 10-digit number.
    existing_numbers = []
    for p in raw_dir.iterdir():
        if p.is_file() and p.suffix.lower() == ".png":
            match = re.match(r'^(\d{10})\.png$', p.name)
            if match:
                existing_numbers.append(int(match.group(1)))

    next_num = max(existing_numbers) + 1 if existing_numbers else 0

    processed_count = 0
    for src_path in image_paths:
        # Check if already numbered.
        if re.match(r'^\d{10}\.png$', src_path.name):
            print(f"Skipped (already numbered): {src_path.name}")
            continue

        # Generate next number.
        num_str = f"{next_num:010d}"
        new_name = num_str + ".png"
        dest_path = src_path.parent / new_name

        try:
            if Image is not None:
                # Convert to PNG.
                with Image.open(src_path) as im:
                    im = im.convert("RGBA")
                    im.save(dest_path, format="PNG")
                # Remove original file.
                src_path.unlink()
            else:
                # Pillow not installed: just rename to .png extension.
                src_path.rename(dest_path)
            print(f"Processed: {src_path.name} -> {new_name}")
            processed_count += 1
            next_num += 1
        except Exception as e:
            print(f"ERROR: failed to process {src_path.name}: {e}")

    print(f"Processed {processed_count} files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
