#!/usr/bin/env python3
"""Kenney Spritesheet Catalog Builder — extracts, analyzes, and catalogs every
tile from all 5 Kenney roguelike spritesheets. Produces catalog.json (machine-
readable metadata) and gallery.html (visual labeling interface).

Usage:
    python3 tile-tools/build_catalog.py

Safe to re-run — preserves human labels in catalog.json.
"""

import base64
import colorsys
import io
import json
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image

TILE_PX = 16
STRIDE_PX = 17  # 16px tile + 1px margin

MVPQUEST_DIR = Path(__file__).resolve().parent.parent / "mvpquest"
TOOL_DIR = Path(__file__).resolve().parent

SHEETS = {
    "base": {
        "path": MVPQUEST_DIR / "assets/2D assets/Roguelike Base Pack/Spritesheet/roguelikeSheet_transparent.png",
        "cols": 57, "rows": 31,
    },
    "indoor": {
        "path": MVPQUEST_DIR / "assets/2D assets/Roguelike Interior Pack/Tilesheets/roguelikeIndoor_transparent.png",
        "cols": 27, "rows": 18,
    },
    "dungeon": {
        "path": MVPQUEST_DIR / "assets/2D assets/Roguelike Dungeon Pack/Spritesheet/roguelikeDungeon_transparent.png",
        "cols": 29, "rows": 18,
    },
    "city": {
        "path": MVPQUEST_DIR / "assets/2D assets/Roguelike City Pack/Tilemap/tilemap.png",
        "cols": 37, "rows": 28,
    },
    "chars": {
        "path": MVPQUEST_DIR / "assets/2D assets/Roguelike Characters Pack/Spritesheet/roguelikeChar_transparent.png",
        "cols": 54, "rows": 12,
    },
}

COLOR_CATEGORIES = [
    "black", "white", "gray", "red", "orange", "yellow",
    "green", "blue", "purple", "brown", "beige", "pink",
]


def categorize_color(r, g, b):
    """Classify an RGB color into a named category using HSL-like analysis."""
    h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
    hue_deg = h * 360

    # Low lightness → black
    if l < 0.15:
        return "black"
    # High lightness, low saturation → white
    if l > 0.85 and s < 0.3:
        return "white"
    # Low saturation → gray
    if s < 0.15:
        if l < 0.5:
            return "gray"
        return "gray" if l < 0.85 else "white"

    # Medium-low saturation warm tones → brown/beige
    if s < 0.45 and (hue_deg < 50 or hue_deg > 330):
        return "beige" if l > 0.55 else "brown"

    # High saturation — classify by hue
    if hue_deg < 15 or hue_deg >= 345:
        return "pink" if l > 0.6 else "red"
    if hue_deg < 40:
        return "orange"
    if hue_deg < 70:
        return "yellow" if l > 0.4 else "brown"
    if hue_deg < 165:
        return "green"
    if hue_deg < 260:
        return "blue"
    if hue_deg < 310:
        return "purple"
    return "pink" if l > 0.6 else "red"


def detect_edges(pixels, width=16):
    """Return a string like 'TBLR' indicating which edges have opaque pixels."""
    edges = ""
    # Top row
    if any(pixels[x, 0][3] > 128 for x in range(width)):
        edges += "T"
    # Bottom row
    if any(pixels[x, width - 1][3] > 128 for x in range(width)):
        edges += "B"
    # Left column
    if any(pixels[0, y][3] > 128 for y in range(width)):
        edges += "L"
    # Right column
    if any(pixels[width - 1, y][3] > 128 for y in range(width)):
        edges += "R"
    return edges


def quantize_color(r, g, b, step=32):
    """Quantize RGB to buckets for top-colors analysis."""
    return (
        (r // step) * step + step // 2,
        (g // step) * step + step // 2,
        (b // step) * step + step // 2,
    )


def edge_signature(pixels, side, width=16):
    """Extract the pixel strip along one edge as a hashable tuple.
    Returns tuple of 16 RGBA tuples. 'side' is 'T','B','L','R'."""
    if side == "T":
        return tuple(pixels[x, 0] for x in range(width))
    elif side == "B":
        return tuple(pixels[x, width - 1] for x in range(width))
    elif side == "L":
        return tuple(pixels[0, y] for y in range(width))
    elif side == "R":
        return tuple(pixels[width - 1, y] for y in range(width))


def edge_is_transparent(sig):
    """True if every pixel in an edge signature is fully transparent."""
    return all(px[3] == 0 for px in sig)


def analyze_tile(tile_img):
    """Analyze a 16x16 tile image and return metadata dict."""
    pixels = tile_img.load()
    total = TILE_PX * TILE_PX

    opaque_pixels = []
    color_counts = Counter()

    for y in range(TILE_PX):
        for x in range(TILE_PX):
            r, g, b, a = pixels[x, y]
            if a > 128:
                opaque_pixels.append((r, g, b))
                color_counts[quantize_color(r, g, b)] += 1

    opacity = len(opaque_pixels) / total

    if not opaque_pixels:
        return {"is_empty": True, "opacity": 0.0}

    avg_r = sum(p[0] for p in opaque_pixels) // len(opaque_pixels)
    avg_g = sum(p[1] for p in opaque_pixels) // len(opaque_pixels)
    avg_b = sum(p[2] for p in opaque_pixels) // len(opaque_pixels)

    top_colors = [
        "#{:02x}{:02x}{:02x}".format(*c)
        for c, _ in color_counts.most_common(3)
    ]

    return {
        "is_empty": False,
        "opacity": round(opacity, 3),
        "is_solid": opacity > 0.95,
        "avg_color": "#{:02x}{:02x}{:02x}".format(avg_r, avg_g, avg_b),
        "color_category": categorize_color(avg_r, avg_g, avg_b),
        "edges": detect_edges(pixels),
        "top_colors": top_colors,
        "edge_sigs": {
            "T": edge_signature(pixels, "T"),
            "B": edge_signature(pixels, "B"),
            "L": edge_signature(pixels, "L"),
            "R": edge_signature(pixels, "R"),
        },
    }


def opacity_bucket(opacity):
    """Classify opacity into a named bucket."""
    if opacity == 0:
        return "empty"
    if opacity < 0.33:
        return "sparse"
    if opacity <= 0.80:
        return "partial"
    return "solid"


def load_existing_labels(catalog_path):
    """Load existing catalog.json and return dicts of preserved labels."""
    tile_labels = {}
    cluster_labels = {}
    if catalog_path.exists():
        try:
            data = json.loads(catalog_path.read_text())
            for tile_id, tile in data.get("tiles", {}).items():
                preserved = {}
                if tile.get("label"):
                    preserved["label"] = tile["label"]
                if tile.get("tags"):
                    preserved["tags"] = tile["tags"]
                if preserved:
                    tile_labels[tile_id] = preserved
            for cluster_id, cluster in data.get("clusters", {}).items():
                preserved = {}
                if cluster.get("label"):
                    preserved["label"] = cluster["label"]
                if cluster.get("description"):
                    preserved["description"] = cluster["description"]
                if preserved:
                    cluster_labels[cluster_id] = preserved
        except (json.JSONDecodeError, KeyError):
            print("Warning: Could not parse existing catalog.json, starting fresh")
    return tile_labels, cluster_labels


def build_catalog():
    """Main pipeline: extract, analyze, cluster, output."""
    t0 = time.time()
    catalog_path = TOOL_DIR / "catalog.json"
    gallery_path = TOOL_DIR / "gallery.html"

    # Load existing labels
    tile_labels, cluster_labels = load_existing_labels(catalog_path)

    # Stage 1: Extract & Analyze
    all_tiles = {}
    sheet_meta = {}
    sheet_images = {}

    for sheet_name, sheet_info in SHEETS.items():
        path = sheet_info["path"]
        if not path.exists():
            print(f"Error: Sheet not found: {path}", file=sys.stderr)
            sys.exit(1)

        img = Image.open(path).convert("RGBA")
        sheet_images[sheet_name] = img
        cols, rows = sheet_info["cols"], sheet_info["rows"]
        non_empty = 0

        for row in range(rows):
            for col in range(cols):
                x = col * STRIDE_PX
                y = row * STRIDE_PX
                tile_img = img.crop((x, y, x + TILE_PX, y + TILE_PX))
                meta = analyze_tile(tile_img)

                tile_id = f"{sheet_name}:{col}:{row}"

                if meta["is_empty"]:
                    continue

                non_empty += 1
                bucket = opacity_bucket(meta["opacity"])
                cluster_key = f"{sheet_name}/{meta['color_category']}/{bucket}"

                tile_entry = {
                    "sheet": sheet_name,
                    "col": col,
                    "row": row,
                    "opacity": meta["opacity"],
                    "is_solid": meta.get("is_solid", False),
                    "avg_color": meta["avg_color"],
                    "color_category": meta["color_category"],
                    "edges": meta["edges"],
                    "top_colors": meta["top_colors"],
                    "cluster": cluster_key,
                    "label": "",
                    "tags": [],
                    "_edge_sigs": meta["edge_sigs"],  # temp, not serialized
                }

                # Merge preserved labels
                if tile_id in tile_labels:
                    tile_entry.update(tile_labels[tile_id])

                all_tiles[tile_id] = tile_entry

        sheet_meta[sheet_name] = {
            "path": str(path.relative_to(MVPQUEST_DIR.parent)),
            "cols": cols,
            "rows": rows,
            "total": cols * rows,
            "non_empty": non_empty,
        }
        print(f"  {sheet_name}: {non_empty}/{cols * rows} non-empty tiles")

    # Stage 2: Cluster
    clusters = {}
    for tile_id, tile in all_tiles.items():
        key = tile["cluster"]
        if key not in clusters:
            clusters[key] = {
                "auto_name": key.replace("/", " / "),
                "label": "",
                "description": "",
                "count": 0,
            }
        clusters[key]["count"] += 1

    # Merge preserved cluster labels
    for cluster_id, preserved in cluster_labels.items():
        if cluster_id in clusters:
            clusters[cluster_id].update(preserved)

    # Stage 2b: Edge matching — find tile neighbors
    print("\n  Building edge index...")

    # Build index: edge_signature -> list of (tile_id, side)
    # "right" edges match "left" edges; "bottom" edges match "top" edges
    # Index by the "accepting" side: L edges and T edges
    left_index = {}   # sig -> [tile_id, ...]  (tiles that accept on their left)
    top_index = {}    # sig -> [tile_id, ...]  (tiles that accept on their top)
    right_index = {}  # sig -> [tile_id, ...]
    bottom_index = {} # sig -> [tile_id, ...]

    for tile_id, tile in all_tiles.items():
        sigs = tile["_edge_sigs"]
        for side, index in [("L", left_index), ("R", right_index),
                            ("T", top_index), ("B", bottom_index)]:
            sig = sigs[side]
            if not edge_is_transparent(sig):
                if sig not in index:
                    index[sig] = []
                index[sig].append(tile_id)

    # Filter out overly-common edge signatures — these are generic edges
    # (e.g., solid gray row) that bridge unrelated tilesets.
    MAX_EDGE_FREQ = 12  # if an edge sig appears on >12 tiles, it's too generic
    all_sig_counts = Counter()
    for idx in [left_index, right_index, top_index, bottom_index]:
        for sig, tiles_list in idx.items():
            all_sig_counts[sig] += len(tiles_list)
    generic_sigs = {sig for sig, count in all_sig_counts.items() if count > MAX_EDGE_FREQ}
    if generic_sigs:
        print(f"  Filtered {len(generic_sigs)} generic edge signatures (>{MAX_EDGE_FREQ} occurrences)")

    # For each tile, find neighbors (tiles whose edge pixels match exactly)
    neighbors = {}  # tile_id -> {R: [...], L: [...], T: [...], B: [...]}
    match_count = 0
    for tile_id, tile in all_tiles.items():
        sigs = tile["_edge_sigs"]
        tile_neighbors = {"R": [], "L": [], "T": [], "B": []}

        # My right edge matches tiles whose left edge is the same
        r_sig = sigs["R"]
        if not edge_is_transparent(r_sig) and r_sig not in generic_sigs and r_sig in left_index:
            tile_neighbors["R"] = [t for t in left_index[r_sig] if t != tile_id]

        # My left edge matches tiles whose right edge is the same
        l_sig = sigs["L"]
        if not edge_is_transparent(l_sig) and l_sig not in generic_sigs and l_sig in right_index:
            tile_neighbors["L"] = [t for t in right_index[l_sig] if t != tile_id]

        # My bottom edge matches tiles whose top edge is the same
        b_sig = sigs["B"]
        if not edge_is_transparent(b_sig) and b_sig not in generic_sigs and b_sig in top_index:
            tile_neighbors["B"] = [t for t in top_index[b_sig] if t != tile_id]

        # My top edge matches tiles whose bottom edge is the same
        t_sig = sigs["T"]
        if not edge_is_transparent(t_sig) and t_sig not in generic_sigs and t_sig in bottom_index:
            tile_neighbors["T"] = [t for t in bottom_index[t_sig] if t != tile_id]

        has_any = any(tile_neighbors[s] for s in "TBLR")
        if has_any:
            neighbors[tile_id] = tile_neighbors
            match_count += sum(len(v) for v in tile_neighbors.values())

    print(f"  Found {len(neighbors)} tiles with edge matches ({match_count} connections)")

    # Stage 2c: Build tileset families via union-find
    parent = {}

    def find(x):
        while parent.get(x, x) != x:
            parent[x] = parent.get(parent[x], parent[x])
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    for tile_id, nbrs in neighbors.items():
        for side_list in nbrs.values():
            for other_id in side_list:
                # Only group tiles from the same sheet into families
                if all_tiles[tile_id]["sheet"] == all_tiles[other_id]["sheet"]:
                    union(tile_id, other_id)

    # Collect families
    family_map = {}  # root -> [tile_ids]
    for tile_id in neighbors:
        root = find(tile_id)
        if root not in family_map:
            family_map[root] = []
        family_map[root].append(tile_id)

    # Also include tiles that have no neighbors but are in all_tiles
    # (they'll be singletons — skip them for family grouping)

    # Sort families by size descending, assign IDs
    sorted_families = sorted(family_map.values(), key=len, reverse=True)
    families = {}
    for i, members in enumerate(sorted_families):
        if len(members) < 2:
            continue  # skip singletons
        fam_id = f"family_{i}"
        # Determine dominant sheet and color
        sheet_counts = Counter(all_tiles[t]["sheet"] for t in members)
        color_counts = Counter(all_tiles[t]["color_category"] for t in members)
        families[fam_id] = {
            "id": fam_id,
            "size": len(members),
            "tiles": sorted(members),
            "dominant_sheet": sheet_counts.most_common(1)[0][0],
            "dominant_color": color_counts.most_common(1)[0][0],
            "label": "",
        }
        # Tag each tile with its family
        for t in members:
            all_tiles[t]["family"] = fam_id

    # Set family="" for tiles not in any family
    for tile_id, tile in all_tiles.items():
        if "family" not in tile:
            tile["family"] = ""

    # Store neighbor lists on tiles (only tile IDs, not sigs)
    for tile_id, tile in all_tiles.items():
        nbrs = neighbors.get(tile_id, {"R": [], "L": [], "T": [], "B": []})
        tile["neighbors"] = {s: nbrs[s] for s in "TBLR" if nbrs.get(s)}

    # Clean up temp edge sigs
    for tile in all_tiles.values():
        del tile["_edge_sigs"]

    print(f"  Built {len(families)} tileset families (2+ members)")

    # Stage 3: Write catalog.json
    catalog = {
        "meta": {
            "generated": datetime.now(timezone.utc).isoformat(),
            "version": 2,
            "total_tiles": len(all_tiles),
            "total_clusters": len(clusters),
            "total_families": len(families),
            "sheets": sheet_meta,
        },
        "clusters": dict(sorted(clusters.items())),
        "families": families,
        "tiles": dict(sorted(all_tiles.items())),
    }

    catalog_path.write_text(json.dumps(catalog, indent=2) + "\n")
    print(f"\nWrote {catalog_path} ({len(all_tiles)} tiles, {len(clusters)} clusters)")

    # Stage 4: Generate gallery.html
    html = generate_gallery(all_tiles, clusters, families, sheet_images, sheet_meta)
    gallery_path.write_text(html)
    print(f"Wrote {gallery_path}")

    elapsed = time.time() - t0
    print(f"\nDone in {elapsed:.1f}s")


def sheet_to_data_uri(img):
    """Convert a PIL Image to a base64 data URI."""
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")
    return f"data:image/png;base64,{b64}"


def generate_gallery(tiles, clusters, families, sheet_images, sheet_meta):
    """Generate a self-contained HTML gallery for tile labeling."""
    # Build data URIs for each sheet
    sheet_uris = {}
    for name, img in sheet_images.items():
        sheet_uris[name] = sheet_to_data_uri(img)

    # Build tile data as JSON for embedding
    tiles_json = json.dumps(tiles)
    clusters_json = json.dumps(clusters)
    families_json = json.dumps(families)
    meta_json = json.dumps(sheet_meta)
    uris_json = json.dumps(sheet_uris)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Kenney Tile Catalog — Gallery</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #1a1a2e; color: #e0e0e0; }}
#top-bar {{ background: #16213e; padding: 8px 16px; display: flex; gap: 8px; align-items: center; flex-wrap: wrap; position: sticky; top: 0; z-index: 100; }}
#top-bar button {{ padding: 6px 14px; border: 1px solid #444; background: #0f3460; color: #e0e0e0; border-radius: 4px; cursor: pointer; font-size: 13px; }}
#top-bar button.active {{ background: #e94560; border-color: #e94560; color: #fff; }}
#top-bar button:hover {{ background: #533483; }}
.view-btn.active {{ background: #533483 !important; border-color: #533483 !important; }}
#stats {{ margin-left: auto; font-size: 13px; color: #aaa; }}
#layout {{ display: flex; }}
#sidebar {{ width: 180px; padding: 12px; background: #16213e; height: calc(100vh - 44px); overflow-y: auto; position: sticky; top: 44px; flex-shrink: 0; }}
#sidebar label {{ display: block; padding: 2px 0; font-size: 13px; cursor: pointer; }}
#sidebar input {{ margin-right: 4px; }}
#main {{ flex: 1; padding: 16px; overflow-y: auto; }}
.cluster-section {{ margin-bottom: 24px; }}
.cluster-header {{ background: #16213e; padding: 8px 12px; border-radius: 6px; cursor: pointer; display: flex; justify-content: space-between; align-items: center; }}
.cluster-header:hover {{ background: #1a1a3e; }}
.cluster-header h3 {{ font-size: 14px; font-weight: 600; }}
.cluster-header .count {{ font-size: 12px; color: #888; }}
.cluster-label {{ font-size: 12px; color: #e94560; margin-left: 8px; }}
.tile-grid {{ display: flex; flex-wrap: wrap; gap: 4px; padding: 8px 0; }}
.tile-cell {{ position: relative; cursor: pointer; }}
.tile-cell canvas {{ display: block; border-radius: 2px; }}
.tile-cell canvas:hover {{ outline: 2px solid #e94560; }}
.tile-cell.labeled canvas {{ outline: 2px solid #4ecca3; }}
.tile-cell.highlight canvas {{ outline: 2px solid #ffcc00; }}
.tooltip {{ position: fixed; background: #16213e; border: 1px solid #444; padding: 8px 12px; border-radius: 6px; font-size: 12px; z-index: 200; pointer-events: none; white-space: pre-line; max-width: 300px; }}
.modal-overlay {{ position: fixed; inset: 0; background: rgba(0,0,0,0.6); z-index: 300; display: flex; align-items: center; justify-content: center; }}
.modal {{ background: #16213e; border: 1px solid #444; border-radius: 8px; padding: 20px; width: 500px; max-width: 90vw; max-height: 90vh; overflow-y: auto; }}
.modal h3 {{ margin-bottom: 12px; }}
.modal label {{ display: block; margin-bottom: 4px; font-size: 13px; }}
.modal input, .modal textarea {{ width: 100%; padding: 6px 8px; border: 1px solid #444; background: #1a1a2e; color: #e0e0e0; border-radius: 4px; margin-bottom: 10px; font-family: inherit; }}
.modal textarea {{ height: 60px; resize: vertical; }}
.modal .btn-row {{ display: flex; gap: 8px; justify-content: flex-end; }}
.modal button {{ padding: 6px 16px; border: none; border-radius: 4px; cursor: pointer; font-size: 13px; }}
.modal .btn-save {{ background: #4ecca3; color: #1a1a2e; }}
.modal .btn-cancel {{ background: #444; color: #e0e0e0; }}
.modal .btn-clear {{ background: #e94560; color: #fff; }}
#color-swatch {{ display: inline-block; width: 14px; height: 14px; border-radius: 2px; vertical-align: middle; margin-right: 4px; }}
.neighbor-panel {{ background: #0f1a2e; border: 1px solid #333; border-radius: 8px; padding: 16px; margin-top: 12px; }}
.neighbor-panel h4 {{ font-size: 13px; margin-bottom: 8px; color: #4ecca3; }}
.neighbor-cross {{ display: grid; grid-template-columns: auto auto auto; gap: 4px; justify-items: center; align-items: center; width: fit-content; margin: 0 auto 12px; }}
.neighbor-cross .center-tile canvas {{ outline: 3px solid #e94560; }}
.neighbor-dir {{ text-align: center; }}
.neighbor-dir .dir-label {{ font-size: 11px; color: #888; margin-bottom: 2px; }}
.neighbor-dir .tile-grid {{ justify-content: center; }}
.family-badge {{ display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 11px; background: #533483; color: #e0e0e0; margin-left: 8px; }}
</style>
</head>
<body>

<div id="top-bar">
  <button class="view-btn active" data-view="clusters">Clusters</button>
  <button class="view-btn" data-view="families">Families</button>
  <span style="width:1px;background:#444;height:24px"></span>
  <button class="sheet-btn active" data-sheet="all">All</button>
  <button class="sheet-btn" data-sheet="base">Base</button>
  <button class="sheet-btn" data-sheet="indoor">Indoor</button>
  <button class="sheet-btn" data-sheet="dungeon">Dungeon</button>
  <button class="sheet-btn" data-sheet="city">City</button>
  <button class="sheet-btn" data-sheet="chars">Chars</button>
  <span style="width:1px;background:#444;height:24px"></span>
  <button id="btn-import" title="Import labels from catalog.json">Import</button>
  <button id="btn-export" title="Export labels as catalog.json">Export</button>
  <button id="btn-save" title="Save labels to server" style="background:#4ecca3;color:#1a1a2e;border-color:#4ecca3;">Save to Server</button>
  <div id="stats"></div>
</div>

<div id="layout">
  <div id="sidebar">
    <strong style="font-size:13px;">Color Filter</strong>
    <hr style="border-color:#333;margin:6px 0;">
    <label><input type="checkbox" class="color-cb" value="all" checked> All</label>
  </div>
  <div id="main"></div>
</div>

<div id="tooltip" class="tooltip" style="display:none;"></div>

<script>
window.onerror = function(msg, url, line, col, err) {{
  document.getElementById('stats').textContent = 'JS ERROR: ' + msg + ' (line ' + line + ')';
  document.getElementById('stats').style.color = '#e94560';
}};
const TILES = {tiles_json};
const CLUSTERS = {clusters_json};
const FAMILIES = {families_json};
const SHEET_META = {meta_json};
const SHEET_URIS = {uris_json};
const SCALE = 3;
const TILE_PX = 16;
const STRIDE = 17;
const COLORS = {json.dumps(COLOR_CATEGORIES)};

// State
let activeSheet = 'all';
let activeView = 'clusters';
let activeColors = new Set(COLORS);
let sheetImages = {{}};
let labels = {{}};
let clusterLabels = {{}};

const imagePromises = Object.entries(SHEET_URIS).map(([name, uri]) => {{
  return new Promise(resolve => {{
    const img = new window.Image();
    img.onload = () => {{ sheetImages[name] = img; resolve(); }};
    img.src = uri;
  }});
}});

try {{
  const saved = localStorage.getItem('tile-catalog-labels');
  if (saved) labels = JSON.parse(saved);
  const savedClusters = localStorage.getItem('tile-catalog-cluster-labels');
  if (savedClusters) clusterLabels = JSON.parse(savedClusters);
}} catch(e) {{}}

for (const [tid, t] of Object.entries(TILES)) {{
  if (t.label && !labels[tid]) labels[tid] = {{ label: t.label, tags: t.tags || [] }};
}}
for (const [cid, c] of Object.entries(CLUSTERS)) {{
  if (c.label && !clusterLabels[cid]) clusterLabels[cid] = {{ label: c.label, description: c.description || '' }};
}}

function saveLabels() {{
  localStorage.setItem('tile-catalog-labels', JSON.stringify(labels));
  localStorage.setItem('tile-catalog-cluster-labels', JSON.stringify(clusterLabels));
  updateStats();
}}

function updateStats() {{
  const total = Object.keys(TILES).length;
  const labeled = Object.values(labels).filter(l => l.label).length;
  const famCount = Object.keys(FAMILIES).length;
  document.getElementById('stats').textContent = `${{total}} tiles | ${{labeled}} labeled | ${{famCount}} families`;
}}

function drawTile(canvas, sheetName, col, row, scale) {{
  scale = scale || SCALE;
  const ctx = canvas.getContext('2d');
  const img = sheetImages[sheetName];
  if (!img) return;
  canvas.width = TILE_PX * scale;
  canvas.height = TILE_PX * scale;
  ctx.imageSmoothingEnabled = false;
  const bs = scale * 4;
  for (let y = 0; y < canvas.height; y += bs) {{
    for (let x = 0; x < canvas.width; x += bs) {{
      ctx.fillStyle = ((x + y) / bs) % 2 === 0 ? '#2a2a3a' : '#1e1e2e';
      ctx.fillRect(x, y, bs, bs);
    }}
  }}
  ctx.drawImage(img, col * STRIDE, row * STRIDE, TILE_PX, TILE_PX, 0, 0, TILE_PX * scale, TILE_PX * scale);
}}

function makeTileCell(t, opts) {{
  opts = opts || {{}};
  const cell = document.createElement('div');
  cell.className = 'tile-cell' + (labels[t.id || t] && labels[t.id || t].label ? ' labeled' : '') + (opts.highlight ? ' highlight' : '');
  const tile = typeof t === 'string' ? TILES[t] : t;
  const tid = typeof t === 'string' ? t : t.id;
  if (!tile) return cell;
  const canvas = document.createElement('canvas');
  drawTile(canvas, tile.sheet, tile.col, tile.row, opts.scale);
  cell.appendChild(canvas);
  cell.addEventListener('mouseenter', (e) => showTooltip(e, {{ id: tid, ...tile }}));
  cell.addEventListener('mouseleave', hideTooltip);
  cell.addEventListener('click', (ev) => {{
    ev.stopPropagation();
    showTileModal(tid);
  }});
  return cell;
}}

function renderClusters() {{
  const main = document.getElementById('main');
  main.innerHTML = '';
  const groups = {{}};
  for (const [tid, t] of Object.entries(TILES)) {{
    if (activeSheet !== 'all' && t.sheet !== activeSheet) continue;
    if (!activeColors.has(t.color_category)) continue;
    const ck = t.cluster;
    if (!groups[ck]) groups[ck] = [];
    groups[ck].push({{ id: tid, ...t }});
  }}
  for (const ck of Object.keys(groups).sort()) {{
    const tiles = groups[ck];
    const cluster = CLUSTERS[ck] || {{}};
    const cl = clusterLabels[ck];
    const section = document.createElement('div');
    section.className = 'cluster-section';
    const header = document.createElement('div');
    header.className = 'cluster-header';
    const labelStr = cl && cl.label ? `<span class="cluster-label">${{cl.label}}</span>` : '';
    header.innerHTML = `<h3>${{cluster.auto_name || ck}}${{labelStr}}</h3><span class="count">${{tiles.length}} tiles</span>`;
    header.addEventListener('click', () => showClusterModal(ck));
    section.appendChild(header);
    const grid = document.createElement('div');
    grid.className = 'tile-grid';
    for (const t of tiles) grid.appendChild(makeTileCell(t));
    section.appendChild(grid);
    main.appendChild(section);
  }}
  updateStats();
}}

function renderFamilies() {{
  const main = document.getElementById('main');
  main.innerHTML = '';
  const sortedFams = Object.entries(FAMILIES).sort((a, b) => b[1].size - a[1].size);
  let shown = 0;
  for (const [famId, fam] of sortedFams) {{
    // Filter by active sheet
    const tiles = fam.tiles.filter(tid => {{
      const t = TILES[tid];
      if (!t) return false;
      if (activeSheet !== 'all' && t.sheet !== activeSheet) return false;
      if (!activeColors.has(t.color_category)) return false;
      return true;
    }});
    if (tiles.length < 2) continue;
    shown++;
    const section = document.createElement('div');
    section.className = 'cluster-section';
    const header = document.createElement('div');
    header.className = 'cluster-header';
    header.innerHTML = `<h3>Family ${{shown}}<span class="family-badge">${{fam.dominant_sheet}} / ${{fam.dominant_color}}</span></h3><span class="count">${{tiles.length}} connected tiles</span>`;
    header.addEventListener('click', () => showFamilyModal(famId, tiles));
    section.appendChild(header);
    const grid = document.createElement('div');
    grid.className = 'tile-grid';
    for (const tid of tiles) grid.appendChild(makeTileCell(tid));
    section.appendChild(grid);
    main.appendChild(section);
  }}
  if (shown === 0) {{
    main.innerHTML = '<p style="padding:40px;color:#888;">No families match the current filters.</p>';
  }}
  updateStats();
}}

function render() {{
  if (activeView === 'families') renderFamilies();
  else renderClusters();
}}

function showTooltip(e, t) {{
  const tip = document.getElementById('tooltip');
  const lbl = labels[t.id] && labels[t.id].label ? `\\nLabel: ${{labels[t.id].label}}` : '';
  const tags = labels[t.id] && labels[t.id].tags && labels[t.id].tags.length ? `\\nTags: ${{labels[t.id].tags.join(', ')}}` : '';
  const nbrs = t.neighbors || {{}};
  const nbrCount = Object.values(nbrs).reduce((s, a) => s + a.length, 0);
  const nbrStr = nbrCount > 0 ? `\\nNeighbors: ${{nbrCount}} (${{Object.entries(nbrs).map(([d,a]) => d + ':' + a.length).join(' ')}})` : '';
  const famStr = t.family ? `\\nFamily: ${{t.family}}` : '';
  tip.innerHTML = `<span id="color-swatch" style="background:${{t.avg_color}}"></span>${{t.id}}\\nColor: ${{t.color_category}} (${{t.avg_color}})\\nOpacity: ${{(t.opacity * 100).toFixed(1)}}%\\nEdges: ${{t.edges || 'none'}}${{nbrStr}}${{famStr}}${{lbl}}${{tags}}`;
  tip.style.display = 'block';
  tip.style.left = Math.min(e.clientX + 12, window.innerWidth - 300) + 'px';
  tip.style.top = Math.min(e.clientY + 12, window.innerHeight - 150) + 'px';
}}

function hideTooltip() {{
  document.getElementById('tooltip').style.display = 'none';
}}

function enterToSave(overlay) {{
  overlay.addEventListener('keydown', (e) => {{
    if (e.key === 'Enter' && !e.shiftKey) {{
      e.preventDefault();
      document.getElementById('modal-save').click();
    }}
  }});
}}

function showTileModal(tileId) {{
  try {{
  const t = TILES[tileId];
  if (!t) {{ alert('Tile not found: ' + tileId); return; }}
  const existing = labels[tileId] || {{ label: '', tags: [] }};
  const nbrs = t.neighbors || {{}};
  const hasNeighbors = Object.values(nbrs).some(a => a.length > 0);

  const overlay = document.createElement('div');
  overlay.className = 'modal-overlay';

  const modal = document.createElement('div');
  modal.className = 'modal';

  // Header + label form
  modal.innerHTML = `
    <h3>Tile: ${{tileId}}</h3>
    <p style="font-size:12px;color:#888;margin-bottom:12px;">${{t.color_category}} | ${{(t.opacity*100).toFixed(0)}}% opacity | edges: ${{t.edges}}${{t.family ? ' | ' + t.family : ''}}</p>
    <label>Label</label>
    <input id="modal-label" value="${{existing.label}}" placeholder="e.g. grass, stone wall, tree trunk">
    <label>Tags (comma-separated)</label>
    <input id="modal-tags" value="${{(existing.tags || []).join(', ')}}" placeholder="e.g. terrain, outdoor, tileable">
    <div class="btn-row" style="margin-bottom:12px;">
      <button class="btn-clear" id="modal-clear">Clear</button>
      <button class="btn-cancel" id="modal-cancel">Cancel</button>
      <button class="btn-save" id="modal-save">Save</button>
    </div>`;

  // Neighbor panel
  if (hasNeighbors) {{
    const panel = document.createElement('div');
    panel.className = 'neighbor-panel';
    panel.innerHTML = '<h4>Edge-Matched Neighbors</h4>';

    // Cross layout: center tile with neighbors on each side
    const cross = document.createElement('div');
    cross.className = 'neighbor-cross';

    // Row 1: empty | top | empty
    cross.appendChild(document.createElement('div'));
    const topDiv = document.createElement('div');
    topDiv.className = 'neighbor-dir';
    topDiv.innerHTML = '<div class="dir-label">Top (' + (nbrs.T || []).length + ')</div>';
    const topGrid = document.createElement('div');
    topGrid.className = 'tile-grid';
    topGrid.style.cssText = 'justify-content:center;max-height:120px;overflow-y:auto;';
    for (const nid of (nbrs.T || []).slice(0, 12)) topGrid.appendChild(makeTileCell(nid, {{scale: 2}}));
    topDiv.appendChild(topGrid);
    cross.appendChild(topDiv);
    cross.appendChild(document.createElement('div'));

    // Row 2: left | CENTER | right
    const leftDiv = document.createElement('div');
    leftDiv.className = 'neighbor-dir';
    leftDiv.innerHTML = '<div class="dir-label">Left (' + (nbrs.L || []).length + ')</div>';
    const leftGrid = document.createElement('div');
    leftGrid.className = 'tile-grid';
    leftGrid.style.cssText = 'justify-content:center;max-height:120px;overflow-y:auto;';
    for (const nid of (nbrs.L || []).slice(0, 12)) leftGrid.appendChild(makeTileCell(nid, {{scale: 2}}));
    leftDiv.appendChild(leftGrid);
    cross.appendChild(leftDiv);

    const centerDiv = document.createElement('div');
    centerDiv.className = 'center-tile';
    const centerCanvas = document.createElement('canvas');
    drawTile(centerCanvas, t.sheet, t.col, t.row, 4);
    centerDiv.appendChild(centerCanvas);
    cross.appendChild(centerDiv);

    const rightDiv = document.createElement('div');
    rightDiv.className = 'neighbor-dir';
    rightDiv.innerHTML = '<div class="dir-label">Right (' + (nbrs.R || []).length + ')</div>';
    const rightGrid = document.createElement('div');
    rightGrid.className = 'tile-grid';
    rightGrid.style.cssText = 'justify-content:center;max-height:120px;overflow-y:auto;';
    for (const nid of (nbrs.R || []).slice(0, 12)) rightGrid.appendChild(makeTileCell(nid, {{scale: 2}}));
    rightDiv.appendChild(rightGrid);
    cross.appendChild(rightDiv);

    // Row 3: empty | bottom | empty
    cross.appendChild(document.createElement('div'));
    const botDiv = document.createElement('div');
    botDiv.className = 'neighbor-dir';
    botDiv.innerHTML = '<div class="dir-label">Bottom (' + (nbrs.B || []).length + ')</div>';
    const botGrid = document.createElement('div');
    botGrid.className = 'tile-grid';
    botGrid.style.cssText = 'justify-content:center;max-height:120px;overflow-y:auto;';
    for (const nid of (nbrs.B || []).slice(0, 12)) botGrid.appendChild(makeTileCell(nid, {{scale: 2}}));
    botDiv.appendChild(botGrid);
    cross.appendChild(botDiv);
    cross.appendChild(document.createElement('div'));

    panel.appendChild(cross);
    modal.appendChild(panel);
  }}

  overlay.appendChild(modal);
  document.body.appendChild(overlay);
  document.getElementById('modal-label').focus();
  enterToSave(overlay);
  document.getElementById('modal-save').onclick = () => {{
    const label = document.getElementById('modal-label').value.trim();
    const tags = document.getElementById('modal-tags').value.split(',').map(s => s.trim()).filter(Boolean);
    if (label || tags.length) labels[tileId] = {{ label, tags }};
    else delete labels[tileId];
    saveLabels();
    overlay.remove();
    render();
  }};
  document.getElementById('modal-cancel').onclick = () => overlay.remove();
  document.getElementById('modal-clear').onclick = () => {{
    delete labels[tileId];
    saveLabels();
    overlay.remove();
    render();
  }};
  overlay.addEventListener('click', (e) => {{ if (e.target === overlay) overlay.remove(); }});
  }} catch(err) {{ alert('showTileModal error: ' + err.message + '\\n' + err.stack); }}
}}

function showClusterModal(clusterId) {{
  const c = CLUSTERS[clusterId] || {{}};
  const existing = clusterLabels[clusterId] || {{ label: '', description: '' }};
  const tileCount = Object.values(TILES).filter(t => t.cluster === clusterId).length;
  const overlay = document.createElement('div');
  overlay.className = 'modal-overlay';
  overlay.innerHTML = `
    <div class="modal">
      <h3>Label Cluster: ${{c.auto_name || clusterId}}</h3>
      <p style="font-size:12px;color:#888;margin-bottom:12px;">${{tileCount}} tiles — sets label on all unlabeled tiles in this cluster</p>
      <label>Cluster Label</label>
      <input id="modal-label" value="${{existing.label}}" placeholder="e.g. grass/terrain, stone walls">
      <label>Description</label>
      <textarea id="modal-desc" placeholder="Optional description">${{existing.description}}</textarea>
      <div class="btn-row">
        <button class="btn-clear" id="modal-clear">Clear</button>
        <button class="btn-cancel" id="modal-cancel">Cancel</button>
        <button class="btn-save" id="modal-save">Save</button>
      </div>
    </div>`;
  document.body.appendChild(overlay);
  document.getElementById('modal-label').focus();
  enterToSave(overlay);
  document.getElementById('modal-save').onclick = () => {{
    const label = document.getElementById('modal-label').value.trim();
    const desc = document.getElementById('modal-desc').value.trim();
    if (label || desc) {{
      clusterLabels[clusterId] = {{ label, description: desc }};
      if (label) {{
        for (const [tid, t] of Object.entries(TILES)) {{
          if (t.cluster === clusterId && (!labels[tid] || !labels[tid].label)) {{
            labels[tid] = {{ label, tags: labels[tid]?.tags || [] }};
          }}
        }}
      }}
    }} else {{
      delete clusterLabels[clusterId];
    }}
    saveLabels();
    overlay.remove();
    render();
  }};
  document.getElementById('modal-cancel').onclick = () => overlay.remove();
  document.getElementById('modal-clear').onclick = () => {{
    delete clusterLabels[clusterId];
    saveLabels();
    overlay.remove();
    render();
  }};
  overlay.addEventListener('click', (e) => {{ if (e.target === overlay) overlay.remove(); }});
}}

function showFamilyModal(famId, tileIds) {{
  const fam = FAMILIES[famId] || {{}};
  const unlabeledCount = tileIds.filter(tid => !labels[tid] || !labels[tid].label).length;
  const overlay = document.createElement('div');
  overlay.className = 'modal-overlay';
  overlay.innerHTML = `
    <div class="modal">
      <h3>Label Family: ${{famId}}</h3>
      <p style="font-size:12px;color:#888;margin-bottom:12px;">${{tileIds.length}} tiles (${{unlabeledCount}} unlabeled) — ${{fam.dominant_sheet}} / ${{fam.dominant_color}}</p>
      <label>Label (applied to all unlabeled tiles in this family)</label>
      <input id="modal-label" value="" placeholder="e.g. grass terrain, stone walls, water edges">
      <label>Tags (comma-separated, applied to all unlabeled tiles)</label>
      <input id="modal-tags" value="" placeholder="e.g. terrain, tileable, outdoor">
      <div class="btn-row">
        <button class="btn-clear" id="modal-clear">Clear All</button>
        <button class="btn-cancel" id="modal-cancel">Cancel</button>
        <button class="btn-save" id="modal-save">Apply</button>
      </div>
    </div>`;
  document.body.appendChild(overlay);
  document.getElementById('modal-label').focus();
  enterToSave(overlay);
  document.getElementById('modal-save').onclick = () => {{
    const label = document.getElementById('modal-label').value.trim();
    const tags = document.getElementById('modal-tags').value.split(',').map(s => s.trim()).filter(Boolean);
    if (label) {{
      for (const tid of tileIds) {{
        if (!labels[tid] || !labels[tid].label) {{
          labels[tid] = {{ label, tags: labels[tid]?.tags ? [...labels[tid].tags, ...tags] : tags }};
        }}
      }}
    }}
    saveLabels();
    overlay.remove();
    render();
  }};
  document.getElementById('modal-cancel').onclick = () => overlay.remove();
  document.getElementById('modal-clear').onclick = () => {{
    for (const tid of tileIds) delete labels[tid];
    saveLabels();
    overlay.remove();
    render();
  }};
  overlay.addEventListener('click', (e) => {{ if (e.target === overlay) overlay.remove(); }});
}}

// View mode buttons
document.querySelectorAll('.view-btn').forEach(btn => {{
  btn.addEventListener('click', () => {{
    document.querySelectorAll('.view-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    activeView = btn.dataset.view;
    render();
  }});
}});

// Sheet filter buttons
document.querySelectorAll('.sheet-btn').forEach(btn => {{
  btn.addEventListener('click', () => {{
    document.querySelectorAll('.sheet-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    activeSheet = btn.dataset.sheet;
    render();
  }});
}});

// Color filter checkboxes
const sidebar = document.getElementById('sidebar');
for (const color of COLORS) {{
  const label = document.createElement('label');
  label.innerHTML = `<input type="checkbox" class="color-cb" value="${{color}}" checked> ${{color}}`;
  sidebar.appendChild(label);
}}
sidebar.addEventListener('change', (e) => {{
  if (e.target.value === 'all') {{
    const checked = e.target.checked;
    document.querySelectorAll('.color-cb').forEach(cb => cb.checked = checked);
    activeColors = checked ? new Set(COLORS) : new Set();
  }} else {{
    activeColors = new Set();
    document.querySelectorAll('.color-cb:not([value=all])').forEach(cb => {{
      if (cb.checked) activeColors.add(cb.value);
    }});
    document.querySelector('.color-cb[value=all]').checked = activeColors.size === COLORS.length;
  }}
  render();
}});

// Import/Export
document.getElementById('btn-import').addEventListener('click', () => {{
  const input = document.createElement('input');
  input.type = 'file';
  input.accept = '.json';
  input.onchange = (e) => {{
    const file = e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (ev) => {{
      try {{
        const data = JSON.parse(ev.target.result);
        for (const [tid, t] of Object.entries(data.tiles || {{}})) {{
          if (t.label) labels[tid] = {{ label: t.label, tags: t.tags || [] }};
        }}
        for (const [cid, c] of Object.entries(data.clusters || {{}})) {{
          if (c.label) clusterLabels[cid] = {{ label: c.label, description: c.description || '' }};
        }}
        saveLabels();
        render();
        alert('Labels imported successfully!');
      }} catch(err) {{
        alert('Error parsing JSON: ' + err.message);
      }}
    }};
    reader.readAsText(file);
  }};
  input.click();
}});

document.getElementById('btn-export').addEventListener('click', () => {{
  const exportData = {{
    meta: {{ generated: new Date().toISOString(), version: 2, sheets: SHEET_META }},
    clusters: {{}},
    families: FAMILIES,
    tiles: {{}}
  }};
  for (const [cid, c] of Object.entries(CLUSTERS)) {{
    const cl = clusterLabels[cid] || {{}};
    exportData.clusters[cid] = {{ ...c, label: cl.label || '', description: cl.description || '' }};
  }}
  for (const [tid, t] of Object.entries(TILES)) {{
    const lbl = labels[tid] || {{}};
    exportData.tiles[tid] = {{ ...t, label: lbl.label || '', tags: lbl.tags || [] }};
  }}
  const blob = new Blob([JSON.stringify(exportData, null, 2)], {{ type: 'application/json' }});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'catalog.json';
  a.click();
  URL.revokeObjectURL(url);
}});

document.getElementById('btn-save').addEventListener('click', () => {{
  const exportData = {{
    meta: {{ generated: new Date().toISOString(), version: 2, sheets: SHEET_META }},
    clusters: {{}},
    families: FAMILIES,
    tiles: {{}}
  }};
  for (const [cid, c] of Object.entries(CLUSTERS)) {{
    const cl = clusterLabels[cid] || {{}};
    exportData.clusters[cid] = {{ ...c, label: cl.label || '', description: cl.description || '' }};
  }}
  for (const [tid, t] of Object.entries(TILES)) {{
    const lbl = labels[tid] || {{}};
    exportData.tiles[tid] = {{ ...t, label: lbl.label || '', tags: lbl.tags || [] }};
  }}
  const btn = document.getElementById('btn-save');
  btn.textContent = 'Saving...';
  fetch('/save', {{
    method: 'POST',
    headers: {{ 'Content-Type': 'application/json' }},
    body: JSON.stringify(exportData, null, 2)
  }}).then(r => r.json()).then(data => {{
    btn.textContent = 'Saved! (' + data.tiles + ' tiles)';
    setTimeout(() => btn.textContent = 'Save to Server', 2000);
  }}).catch(err => {{
    btn.textContent = 'Error!';
    alert('Save failed: ' + err.message);
    setTimeout(() => btn.textContent = 'Save to Server', 2000);
  }});
}});

Promise.all(imagePromises).then(() => {{
  render();
}});
</script>
</body>
</html>"""
    return html


if __name__ == "__main__":
    print("Kenney Spritesheet Catalog Builder")
    print("=" * 40)
    build_catalog()
