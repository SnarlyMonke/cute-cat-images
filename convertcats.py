"""Rename images in 'cats' folder to sequential 10-digit numbers.

Converts all PNG and JPG files in the 'cats' folder to PNG format with 10-digit numbering
(e.g., 0000000000.png, 0000000001.png, ...).

Converts all GIF files to GIF format with separate 10-digit numbering 
(e.g., 0000000000.gif, 0000000001.gif, ...).

Each format has its own independent numbering sequence.

Creates two count files:
  - image_count.txt: number of PNGs
  - gif_count.txt: number of GIFs

Usage:
    python convertcats.py

If Pillow is installed (PIL), images will be converted. If it's not installed,
the script will just rename files (keeping original binary format).
"""

#can you believe i totally coded this :)

from __future__ import annotations

import re
from pathlib import Path

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    Image = None  # type: ignore


def process_format(raw_dir: Path, extensions: set[str], output_ext: str, format_name: str) -> int:
    """Process images of a given format, convert, rename, and fill gaps.
    
    Args:
        raw_dir: Directory containing images.
        extensions: Set of file extensions to process (e.g., {".png", ".jpg"}).
        output_ext: Output extension (e.g., ".png", ".gif").
        format_name: Human-readable format name for logging.
    
    Returns:
        Number of files processed.
    """
    # Collect image files (case-insensitive extension match).
    image_paths = [
        p for p in raw_dir.iterdir()
        if p.is_file() and p.suffix.lower() in extensions
    ]

    if not image_paths:
        print(f"No {format_name} images found in {raw_dir}.")
        return 0

    # Find the highest existing 10-digit number for this format.
    existing_numbers = []
    for p in raw_dir.iterdir():
        if p.is_file() and p.suffix.lower() == output_ext:
            match = re.match(rf'^(\d{{10}})\{output_ext}$', p.name)
            if match:
                existing_numbers.append(int(match.group(1)))

    next_num = max(existing_numbers) + 1 if existing_numbers else 0

    processed_count = 0
    for src_path in image_paths:
        # Check if already numbered.
        if re.match(rf'^\d{{10}}\{output_ext}$', src_path.name):
            print(f"Skipped (already numbered): {src_path.name}")
            continue

        # Generate next number.
        num_str = f"{next_num:010d}"
        new_name = num_str + output_ext
        dest_path = src_path.parent / new_name

        try:
            if Image is not None:
                # Open and convert/save in target format.
                with Image.open(src_path) as im:
                    # Handle transparency for PNG.
                    if output_ext.lower() == ".png":
                        im = im.convert("RGBA")
                        im.save(dest_path, format="PNG")
                    else:
                        # For GIF, save as-is or convert palette if needed.
                        im.save(dest_path, format="GIF")
                # Remove original file.
                src_path.unlink()
            else:
                # Pillow not installed: just rename to output extension.
                src_path.rename(dest_path)
            print(f"Processed ({format_name}): {src_path.name} -> {new_name}")
            processed_count += 1
            next_num += 1
        except Exception as e:
            print(f"ERROR: failed to process {src_path.name}: {e}")

    return processed_count


def fill_gaps(raw_dir: Path, output_ext: str, format_name: str) -> None:
    """Fill any gaps in numbering by moving the highest-numbered file down into each missing slot.
    
    Example: if numbers are 0000000000..0000000003, 0000000005..0000000007, then 0000000007
    will be renamed to 0000000004 to eliminate the gap.
    """
    while True:
        numbered_files = sorted(
            (int(m.group(1)), p)
            for p in raw_dir.iterdir()
            if p.is_file() and (m := re.match(rf'^(\d{{10}})\{output_ext}$', p.name))
        )
        if not numbered_files:
            break

        nums = [n for n, _ in numbered_files]
        max_num = nums[-1]
        expected = set(range(0, max_num + 1))
        missing = sorted(expected - set(nums))
        if not missing:
            break

        target = missing[0]
        source = max_num
        source_path = raw_dir / f"{source:010d}{output_ext}"
        target_path = raw_dir / f"{target:010d}{output_ext}"

        # Move highest into the first missing slot.
        try:
            source_path.rename(target_path)
            print(f"Filled gap ({format_name}): {source_path.name} -> {target_path.name}")
        except Exception as e:
            print(f"WARNING: failed to fill gap {target}: {e}")
            break


def main() -> int:
    root = Path(__file__).resolve().parent
    raw_dir = root / "cats"

    if not raw_dir.exists():
        print(f"ERROR: input directory does not exist: {raw_dir}")
        return 1

    # Process PNGs.
    png_processed = process_format(raw_dir, {".png", ".jpg", ".jpeg"}, ".png", "PNG")
    fill_gaps(raw_dir, ".png", "PNG")

    # Process GIFs.
    gif_processed = process_format(raw_dir, {".gif"}, ".gif", "GIF")
    fill_gaps(raw_dir, ".gif", "GIF")

    # Count PNG files.
    png_count = sum(
        1 for p in raw_dir.iterdir()
        if p.is_file() and re.match(r'^\d{10}\.png$', p.name)
    )

    # Count GIF files.
    gif_count = sum(
        1 for p in raw_dir.iterdir()
        if p.is_file() and re.match(r'^\d{10}\.gif$', p.name)
    )

    # Write count files.
    png_count_file = raw_dir / "image_count.txt"
    png_count_file.write_text(str(png_count) + "\n", encoding="utf-8")

    gif_count_file = raw_dir / "gif_count.txt"
    gif_count_file.write_text(str(gif_count) + "\n", encoding="utf-8")

    print(f"\nProcessed {png_processed} PNG files. Total numbered PNGs: {png_count}")
    print(f"Processed {gif_processed} GIF files. Total numbered GIFs: {gif_count}")
    print(f"Count files written: {png_count_file}, {gif_count_file}")

    input()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
