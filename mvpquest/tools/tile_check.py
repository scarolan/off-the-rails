#!/usr/bin/env python3
"""Tile spot-checker for Claude/Shelly — extracts tiles from spritesheets
as scaled-up PNGs that Claude can read with the Read tool.

Usage:
    # Single tile — what's at base sheet (13, 21)?
    python3 mvpquest/tools/tile_check.py base 13 21

    # Region — show a 5×3 block starting at (13, 21)
    python3 mvpquest/tools/tile_check.py base 13 21 --region 5x3

    # Custom output path
    python3 mvpquest/tools/tile_check.py base 13 21 -o /tmp/my_tile.png

Output: Saves a scaled PNG to /tmp/tile_<sheet>_<col>_<row>.png
Then use Claude's Read tool to view it.
"""

import argparse
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

TILE_PX = 16
STRIDE_PX = 17  # 16px tile + 1px margin
SCALE = 12      # 12x scale → 192px per tile, very readable

MVPQUEST_DIR = Path(__file__).resolve().parent.parent

SHEETS = {
    'base':    MVPQUEST_DIR / 'assets/2D assets/Roguelike Base Pack/Spritesheet/roguelikeSheet_transparent.png',
    'indoor':  MVPQUEST_DIR / 'assets/2D assets/Roguelike Interior Pack/Tilesheets/roguelikeIndoor_transparent.png',
    'dungeon': MVPQUEST_DIR / 'assets/2D assets/Roguelike Dungeon Pack/Spritesheet/roguelikeDungeon_transparent.png',
    'city':    MVPQUEST_DIR / 'assets/2D assets/Roguelike City Pack/Tilemap/tilemap.png',
    'chars':   MVPQUEST_DIR / 'assets/2D assets/Roguelike Characters Pack/Spritesheet/roguelikeChar_transparent.png',
}

SHEET_DIMS = {
    'base':    (57, 31),
    'indoor':  (27, 18),
    'dungeon': (29, 18),
    'city':    (37, 28),
    'chars':   (54, 12),
}


def extract_tile(img, col, row):
    """Extract a single 16×16 tile from a spritesheet."""
    x = col * STRIDE_PX
    y = row * STRIDE_PX
    return img.crop((x, y, x + TILE_PX, y + TILE_PX))


def render_single(img, col, row, scale=SCALE):
    """Render a single tile scaled up with a green background for transparency."""
    tile = extract_tile(img, col, row)

    # Create output with checkerboard background (shows transparency)
    size = TILE_PX * scale
    out = Image.new('RGBA', (size, size + 24), (40, 40, 40, 255))

    # Draw checkerboard under tile
    checker = Image.new('RGBA', (size, size), (80, 80, 80, 255))
    draw_c = ImageDraw.Draw(checker)
    block = scale * 2
    for cy in range(0, size, block * 2):
        for cx in range(0, size, block * 2):
            draw_c.rectangle([cx, cy, cx + block - 1, cy + block - 1], fill=(60, 60, 60, 255))
            draw_c.rectangle([cx + block, cy + block, cx + block * 2 - 1, cy + block * 2 - 1],
                             fill=(60, 60, 60, 255))

    # Scale tile with nearest-neighbor and composite over checkerboard
    tile_scaled = tile.resize((size, size), Image.NEAREST)
    checker.paste(tile_scaled, (0, 0), tile_scaled)
    out.paste(checker, (0, 0))

    # Draw label at bottom
    draw = ImageDraw.Draw(out)
    label = f"({col}, {row})"
    draw.text((4, size + 4), label, fill=(0, 255, 0, 255))

    return out


def render_region(img, col, row, width, height, scale=6):
    """Render a region of tiles with grid lines and coordinate labels."""
    cell = TILE_PX * scale
    label_h = 16  # height for column labels at top
    label_w = 28  # width for row labels at left

    out_w = label_w + width * (cell + 1)
    out_h = label_h + height * (cell + 1)
    out = Image.new('RGBA', (out_w, out_h), (30, 30, 30, 255))
    draw = ImageDraw.Draw(out)

    max_cols, max_rows = SHEET_DIMS.get(args.sheet, (999, 999))

    for dy in range(height):
        for dx in range(width):
            tc = col + dx
            tr = row + dy
            px = label_w + dx * (cell + 1)
            py = label_h + dy * (cell + 1)

            if tc < max_cols and tr < max_rows:
                tile = extract_tile(img, tc, tr)
                tile_scaled = tile.resize((cell, cell), Image.NEAREST)

                # Checkerboard background for transparency
                for cy2 in range(0, cell, scale * 2):
                    for cx2 in range(0, cell, scale * 2):
                        draw.rectangle(
                            [px + cx2, py + cy2,
                             px + cx2 + scale - 1, py + cy2 + scale - 1],
                            fill=(50, 50, 50, 255))
                        draw.rectangle(
                            [px + cx2 + scale, py + cy2 + scale,
                             px + cx2 + scale * 2 - 1, py + cy2 + scale * 2 - 1],
                            fill=(50, 50, 50, 255))

                out.paste(tile_scaled, (px, py), tile_scaled)
            else:
                # Out of bounds
                draw.rectangle([px, py, px + cell - 1, py + cell - 1], fill=(20, 20, 20))
                draw.line([px, py, px + cell - 1, py + cell - 1], fill=(60, 30, 30))

            # Grid border
            draw.rectangle([px, py, px + cell, py + cell], outline=(80, 80, 80))

    # Column labels
    for dx in range(width):
        px = label_w + dx * (cell + 1) + cell // 2 - 4
        draw.text((px, 2), str(col + dx), fill=(150, 150, 150))

    # Row labels
    for dy in range(height):
        py = label_h + dy * (cell + 1) + cell // 2 - 4
        draw.text((2, py), str(row + dy), fill=(150, 150, 150))

    return out


def main():
    global args
    parser = argparse.ArgumentParser(description='Extract and view spritesheet tiles')
    parser.add_argument('sheet', choices=SHEETS.keys(), help='Spritesheet name')
    parser.add_argument('col', type=int, help='Tile column (0-indexed)')
    parser.add_argument('row', type=int, help='Tile row (0-indexed)')
    parser.add_argument('--region', '-r', type=str, default=None,
                        help='Region size as WxH (e.g. 5x3). Shows a block of tiles.')
    parser.add_argument('-o', '--output', type=str, default=None,
                        help='Output file path (default: /tmp/tile_<sheet>_<col>_<row>.png)')
    args = parser.parse_args()

    sheet_path = SHEETS[args.sheet]
    if not sheet_path.exists():
        print(f"Error: Spritesheet not found: {sheet_path}", file=sys.stderr)
        sys.exit(1)

    img = Image.open(sheet_path).convert('RGBA')

    if args.region:
        # Parse WxH
        try:
            rw, rh = args.region.lower().split('x')
            rw, rh = int(rw), int(rh)
        except ValueError:
            print(f"Error: Invalid region format '{args.region}', use WxH (e.g. 5x3)", file=sys.stderr)
            sys.exit(1)
        result = render_region(img, args.col, args.row, rw, rh)
        suffix = f"_{rw}x{rh}"
    else:
        result = render_single(img, args.col, args.row)
        suffix = ""

    if args.output:
        out_path = args.output
    else:
        out_path = f"/tmp/tile_{args.sheet}_{args.col}_{args.row}{suffix}.png"

    result.save(out_path)
    print(f"Saved: {out_path}")
    print(f"Use Claude's Read tool to view: {out_path}")


if __name__ == '__main__':
    main()
