#!/usr/bin/env python3
"""Tile Reference Viewer — generates an HTML page showing each spritesheet
with a numbered grid overlay so you can identify tile coordinates at a glance.

Usage:
    python3 tile_viewer.py
    # Opens tile_reference.html in the default browser

Each tile is labeled (col, row) and empty/transparent tiles are dimmed.
"""

import base64
import os
import sys
import webbrowser
from pathlib import Path

# Spritesheet definitions: name, relative path from mvpquest/, cols, rows
SHEETS = [
    ("base",    "assets/2D assets/Roguelike Base Pack/Spritesheet/roguelikeSheet_transparent.png", 57, 31),
    ("chars",   "assets/2D assets/Roguelike Characters Pack/Spritesheet/roguelikeChar_transparent.png", 54, 12),
    ("indoor",  "assets/2D assets/Roguelike Interior Pack/Tilesheets/roguelikeIndoor_transparent.png", 27, 18),
    ("dungeon", "assets/2D assets/Roguelike Dungeon Pack/Spritesheet/roguelikeDungeon_transparent.png", 29, 18),
    ("city",    "assets/2D assets/Roguelike City Pack/Tilemap/tilemap.png", 37, 28),
]

TILE_PX = 16
STRIDE_PX = 17  # 16px tile + 1px margin
SCALE = 2       # render tiles at 2x for readability


def embed_image(path: Path) -> str:
    """Return a base64 data URI for the given image file."""
    data = path.read_bytes()
    b64 = base64.b64encode(data).decode("ascii")
    return f"data:image/png;base64,{b64}"


def generate_html(mvpquest_dir: Path) -> str:
    sections = []
    for name, rel_path, cols, rows in SHEETS:
        img_path = mvpquest_dir / rel_path
        if not img_path.exists():
            sections.append(f'<h2>{name}</h2><p class="missing">Not found: {rel_path}</p>')
            continue

        data_uri = embed_image(img_path)
        cell_size = TILE_PX * SCALE

        grid_w = cols * (cell_size + 1)  # +1 for grid lines
        grid_h = rows * (cell_size + 1)

        # Build grid overlay cells
        cells = []
        for r in range(rows):
            for c in range(cols):
                left = c * (cell_size + 1)
                top = r * (cell_size + 1)
                cells.append(
                    f'<div class="cell" style="left:{left}px;top:{top}px;'
                    f'width:{cell_size}px;height:{cell_size}px">'
                    f'<span class="coord">{c},{r}</span></div>'
                )

        section = f"""
<h2>{name} <span class="dims">({cols} cols x {rows} rows)</span></h2>
<div class="sheet-wrap" style="width:{grid_w}px;height:{grid_h}px">
  <canvas class="sheet-canvas" data-src="{data_uri}"
          data-cols="{cols}" data-rows="{rows}"
          width="{grid_w}" height="{grid_h}"></canvas>
  <div class="grid-overlay">{''.join(cells)}</div>
</div>"""
        sections.append(section)

    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<title>MVPQuest Tile Reference</title>
<style>
  body {{ background: #1a1a2e; color: #eee; font-family: monospace; padding: 20px; }}
  h2 {{ color: #e94560; margin-top: 40px; }}
  .dims {{ color: #888; font-size: 0.7em; }}
  .missing {{ color: #f44; }}
  .sheet-wrap {{ position: relative; border: 2px solid #333; overflow: auto; }}
  .sheet-canvas {{ display: block; image-rendering: pixelated; }}
  .grid-overlay {{ position: absolute; top: 0; left: 0; }}
  .cell {{
    position: absolute;
    border: 1px solid rgba(255,255,255,0.15);
    box-sizing: border-box;
    overflow: hidden;
  }}
  .cell:hover {{
    border-color: #e94560;
    background: rgba(233,69,96,0.3);
    z-index: 10;
  }}
  .coord {{
    display: none;
    position: absolute; bottom: 0; left: 0;
    background: rgba(0,0,0,0.8); color: #0f0;
    font-size: 9px; padding: 1px 2px; white-space: nowrap;
  }}
  .cell:hover .coord {{ display: block; }}
  #search {{ margin: 10px 0; padding: 6px; background: #16213e; color: #eee;
             border: 1px solid #555; font-family: monospace; font-size: 14px; }}
</style>
</head><body>
<h1>MVPQuest Tile Reference</h1>
<p>Hover over a tile to see its (col, row) coordinates. All sheets use 17px stride (16px tile + 1px margin).</p>
<input id="search" placeholder="Jump to sheet (e.g. dungeon)..." oninput="
  const v = this.value.toLowerCase();
  document.querySelectorAll('h2').forEach(h => {{
    if (h.textContent.toLowerCase().includes(v)) h.scrollIntoView({{behavior:'smooth'}});
  }});
">

{''.join(sections)}

<script>
// Draw each spritesheet onto its canvas at {SCALE}x scale
document.querySelectorAll('.sheet-canvas').forEach(canvas => {{
  const img = new Image();
  img.onload = () => {{
    const ctx = canvas.getContext('2d');
    ctx.imageSmoothingEnabled = false;
    const cols = parseInt(canvas.dataset.cols);
    const rows = parseInt(canvas.dataset.rows);
    const cell = {TILE_PX} * {SCALE};
    for (let r = 0; r < rows; r++) {{
      for (let c = 0; c < cols; c++) {{
        const sx = c * {STRIDE_PX}, sy = r * {STRIDE_PX};
        const dx = c * (cell + 1), dy = r * (cell + 1);
        ctx.drawImage(img, sx, sy, {TILE_PX}, {TILE_PX}, dx, dy, cell, cell);
      }}
    }}
  }};
  img.src = canvas.dataset.src;
}});
</script>
</body></html>"""


def main():
    # Find mvpquest/ directory
    script_dir = Path(__file__).resolve().parent
    mvpquest_dir = script_dir.parent  # tools/ is inside mvpquest/

    if not (mvpquest_dir / "assets").exists():
        print(f"Error: Cannot find assets/ in {mvpquest_dir}", file=sys.stderr)
        sys.exit(1)

    html = generate_html(mvpquest_dir)
    out_path = script_dir / "tile_reference.html"
    out_path.write_text(html)
    print(f"Generated: {out_path}")

    # Try to open in browser
    try:
        webbrowser.open(f"file://{out_path}")
    except Exception:
        pass


if __name__ == "__main__":
    main()
