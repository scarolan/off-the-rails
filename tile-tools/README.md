# Kenney Tile Catalog Tools

Automated pipeline that extracts, analyzes, and catalogs every tile from
the 5 Kenney roguelike spritesheets used in MVPQuest.

## Quick Start

```bash
python3 tile-tools/build_catalog.py
```

## Outputs

- **catalog.json** — machine-readable tile metadata + human labels (commit this)
- **gallery.html** — open in browser to visually browse and label tiles

## Re-running

Safe to re-run at any time. Human-added labels, tags, and descriptions in
catalog.json are preserved across rebuilds.

## Using in Claude Sessions

Read `catalog.json` to find tiles by color category, cluster, or label:

```python
import json
catalog = json.loads(open('tile-tools/catalog.json').read())
# Find all green solid tiles in the base sheet
green = [t for t in catalog['tiles'].values()
         if t['sheet'] == 'base' and t['color_category'] == 'green' and t['is_solid']]
```

Use `mvpquest/tools/tile_check.py` to visually verify individual tiles:

```bash
python3 mvpquest/tools/tile_check.py base 5 1
```

## Human Labeling Workflow

1. Run `build_catalog.py` to generate gallery.html
2. Open gallery.html in a browser
3. Click clusters to batch-label groups, or click individual tiles
4. Export labels → save as catalog.json in this directory
5. Commit to repo — future Claude sessions read labels instead of guessing
