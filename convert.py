"""Convert/copy images from "raw images" into "renamed files".

For each PNG/JPG/JPEG image found in "raw images", this script creates a copy named
"cat_{n}.png" in the "renamed files" folder (where n is 1-based).

It also writes a text file in "renamed files" with a single number indicating how many
images were processed.

Usage:
    python convert.py

If Pillow is installed (PIL), JPG/JPEG images will be converted to PNG. If it's not
installed, the script will just copy files and keep their original format extension.
"""

from __future__ import annotations

import os
from pathlib import Path
import shutil
import sys

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    Image = None  # type: ignore


def main() -> int:
    root = Path(__file__).resolve().parent
    raw_dir = root / "raw images"
    out_dir = root / "renamed files"

    out_dir.mkdir(parents=True, exist_ok=True)

    if not raw_dir.exists():
        print(f"ERROR: input directory does not exist: {raw_dir}")
        return 1

    # Collect image files (case-insensitive extension match).
    image_paths = sorted(
        p for p in raw_dir.iterdir()
        if p.is_file() and p.suffix.lower() in {".png", ".jpg", ".jpeg"}
    )

    if not image_paths:
        print(f"No PNG/JPG images found in {raw_dir}.")

    count = 0
    for idx, src_path in enumerate(image_paths, start=1):
        dest_name = f"cat_{idx}.png"
        dest_path = out_dir / dest_name

        if Image is not None:
            # Convert to PNG (if required) or just save.
            try:
                with Image.open(src_path) as im:
                    im = im.convert("RGBA")
                    im.save(dest_path, format="PNG")
            except Exception as e:
                print(f"WARNING: failed to convert {src_path} to PNG: {e}")
                # Fallback: copy as-is with new name, preserving original extension.
                fallback = out_dir / f"cat_{idx}{src_path.suffix.lower()}"
                shutil.copy2(src_path, fallback)
                dest_path = fallback
        else:
            # Pillow not installed: just copy with .png extension for consistency.
            try:
                shutil.copy2(src_path, dest_path)
            except Exception as e:
                print(f"WARNING: failed to copy {src_path} -> {dest_path}: {e}")
                continue

        count += 1

    # Write count file.
    count_file = out_dir / "image_count.txt"
    count_file.write_text(str(count) + "\n", encoding="utf-8")

    print(f"Processed {count} images into '{out_dir}'")
    print(f"Count written to: {count_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
