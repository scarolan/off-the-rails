# MVPQuest Tile Atlas

Reference for all Kenney Roguelike spritesheet tiles used in MVPQuest.
Coordinates are **(col, row)** — pixel offset = `col * 17, row * 17` (16px tiles, 1px margin).

---

## Spritesheets

| Key  | File | Cols × Rows | Notes |
|------|------|-------------|-------|
| `base` | `Roguelike Base Pack/.../roguelikeSheet_transparent.png` | 57 × 31 | Terrain, vegetation, buildings, items, UI |
| `indoor` | `Roguelike Interior Pack/.../roguelikeIndoor_transparent.png` | 27 × 18 | Office/home furniture, indoor walls/floors |
| `dungeon` | `Roguelike Dungeon Pack/.../roguelikeDungeon_transparent.png` | 29 × 18 | Stone walls, cave terrain, dungeon props |
| `city` | `Roguelike City Pack/Tilemap/tilemap.png` | 37 × 28 | Modern city tiles (roads, vehicles, etc.) |
| `chars` | `Roguelike Characters Pack/.../roguelikeChar_transparent.png` | 54 × 12 | Layered character sprites (17px stride) |

---

## Currently Used Tiles

### Ground Layer (non-blocking terrain)

| Constant | ID | Sheet | (c,r) | Description |
|----------|----|-------|-------|-------------|
| `GRASS` | 1 | base | (5,1) | Main grass — bright green |
| `GRASS2` | 2 | base | (3,1) | Grass variant — slightly different shade |
| `WATER` | 3 | base | (1,1) | Deep water center |
| `SAND` | 4 | base | (5,0) | Sand/beach |
| `PATH` | 5 | base | (4,1) | Dirt path — light brown |
| `FLOOR_W` | 30 | indoor | (0,8) | Wood plank floor (office/shrine interior) |
| `STONE_F` | 50 | dungeon | (0,8) | Stone slab floor (dungeon/server interior) |

### Water Edges (ground layer, blocking)

| Constant | ID | Sheet | (c,r) | Position |
|----------|----|-------|-------|----------|
| `WATER_TL` | 60 | base | (0,0) | Shore top-left corner |
| `WATER_T` | 61 | base | (1,0) | Shore top edge |
| `WATER_TR` | 62 | base | (2,0) | Shore top-right corner |
| `WATER_L` | 63 | base | (0,1) | Shore left edge |
| `WATER_R` | 64 | base | (2,1) | Shore right edge |
| `WATER_BL` | 65 | base | (0,2) | Shore bottom-left corner |
| `WATER_B` | 66 | base | (1,2) | Shore bottom edge |
| `WATER_BR` | 67 | base | (2,2) | Shore bottom-right corner |

### Vegetation (objects layer)

| Constant | ID | Sheet | (c,r) | Description |
|----------|----|-------|-------|-------------|
| `TREE_TOP` | 15 | base | (7,4) | Deciduous tree canopy (top half, blocking) |
| `TREE` | 10 | base | (7,5) | Deciduous tree trunk (bottom half, blocking) |
| `PINE_TOP` | 16 | base | (9,4) | Pine/conifer canopy (top half, blocking) |
| `PINE` | 11 | base | (9,5) | Pine/conifer trunk (bottom half, blocking) |
| `BUSH` | 12 | base | (11,5) | Green bush (blocking) |
| `ROCK` | 13 | base | (4,6) | Gray boulder (blocking) |
| `FLOWER` | 14 | base | (14,5) | Small flower (NON-blocking decoration) |

### Building Exterior — Old City-Pack Walls (still in data.js, no longer on campus)

| Constant | ID | Sheet | (c,r) | Description |
|----------|----|-------|-------|-------------|
| `WALL_TL` | 90 | city | (8,0) | Gray wall top-left corner |
| `WALL_T` | 20 | city | (10,0) | Gray wall top edge |
| `WALL_TR` | 91 | city | (9,0) | Gray wall top-right corner |
| `WALL_L` | 92 | city | (11,0) | Gray wall left edge |
| `WALL_F` | 21 | city | (10,1) | Gray wall face/front |
| `WALL_R` | 93 | city | (11,1) | Gray wall right edge |
| `WALL_BL` | 94 | city | (8,1) | Gray wall bottom-left corner |
| `WALL_B` | 95 | city | (10,1) | Gray wall bottom edge |
| `WALL_BR` | 96 | city | (9,1) | Gray wall bottom-right corner |

### Building Exterior — Beige A-Frame (base pack)

| Constant | ID | Sheet | (c,r) | Description |
|----------|----|-------|-------|-------------|
| `BLDG_B_PEAK_L` | 100 | base | (13,21) | Peaked roof left — transparent upper-right triangle |
| `BLDG_B_PEAK_R` | 101 | base | (14,21) | Peaked roof right — transparent upper-left triangle |
| `BLDG_B_ROOF` | 102 | base | (18,21) | Roof fill — solid center tile |
| `BLDG_B_WALL_L` | 103 | base | (13,22) | Wall left edge |
| `BLDG_B_WALL_R` | 104 | base | (14,22) | Wall right edge |
| `BLDG_B_WALL` | 105 | base | (18,22) | Wall fill — solid center |
| `BLDG_B_WIN_L` | 106 | base | (15,22) | Window left half — large opening |
| `BLDG_B_WIN_R` | 107 | base | (16,22) | Window right half — frame visible |
| `BLDG_B_FACE_L` | 108 | base | (13,23) | Front face left edge |
| `BLDG_B_FACE_R` | 109 | base | (14,23) | Front face right edge |
| `BLDG_B_FACE` | 110 | base | (18,23) | Front face fill — solid |
| `BLDG_B_DOOR_L` | 111 | base | (15,23) | Arched door left half (NON-blocking) |
| `BLDG_B_DOOR_R` | 112 | base | (16,23) | Arched door right half (NON-blocking) |

### Building Exterior — Brown/Wood A-Frame (base pack)

| Constant | ID | Sheet | (c,r) | Description |
|----------|----|-------|-------|-------------|
| `BLDG_W_PEAK_L` | 113 | base | (20,21) | Peaked roof left |
| `BLDG_W_PEAK_R` | 114 | base | (21,21) | Peaked roof right |
| `BLDG_W_ROOF` | 115 | base | (25,21) | Roof fill |
| `BLDG_W_WALL_L` | 116 | base | (20,22) | Wall left edge |
| `BLDG_W_WALL_R` | 117 | base | (21,22) | Wall right edge |
| `BLDG_W_WALL` | 118 | base | (25,22) | Wall fill |
| `BLDG_W_FACE_L` | 119 | base | (20,23) | Front face left edge |
| `BLDG_W_FACE_R` | 120 | base | (21,23) | Front face right edge |
| `BLDG_W_FACE` | 121 | base | (25,23) | Front face fill |
| `BLDG_W_DOOR` | 122 | base | (22,22) | Single-tile door opening (NON-blocking) |

### Doors & Special Entrances

| Constant | ID | Sheet | (c,r) | Description |
|----------|----|-------|-------|-------------|
| `DOOR_EXT` | 24 | base | (30,6) | Generic exterior door (arched, wooden) |
| `DOOR_INT` | 35 | indoor | (10,5) | Interior door (wooden, paneled) |
| `CAVE` | 29 | dungeon | (14,5) | Cave mouth entrance (dark opening) |

### Indoor Walls (office/shrine interiors)

| Constant | ID | Sheet | (c,r) | Description |
|----------|----|-------|-------|-------------|
| `WALL_I_TL` | 70 | indoor | (7,4) | Indoor wall top-left corner |
| `WALL_I_T` | 33 | indoor | (8,4) | Indoor wall top edge |
| `WALL_I_TR` | 71 | indoor | (9,4) | Indoor wall top-right corner |
| `WALL_I_L` | 72 | indoor | (7,4) | Indoor wall left edge |
| `WALL_I_F` | 34 | indoor | (8,5) | Indoor wall face/front |
| `WALL_I_R` | 73 | indoor | (9,5) | Indoor wall right edge |
| `WALL_I_BL` | 74 | indoor | (7,6) | Indoor wall bottom-left corner |
| `WALL_I_B` | 75 | indoor | (8,6) | Indoor wall bottom edge |
| `WALL_I_BR` | 76 | indoor | (9,6) | Indoor wall bottom-right corner |

### Stone/Dungeon Walls (server room, dungeon interiors)

| Constant | ID | Sheet | (c,r) | Description |
|----------|----|-------|-------|-------------|
| `STONE_W_TL` | 80 | dungeon | (17,3) | Stone wall top-left corner |
| `STONE_W_T` | 51 | dungeon | (18,3) | Stone wall top edge |
| `STONE_W_TR` | 81 | dungeon | (19,3) | Stone wall top-right corner |
| `STONE_W_L` | 82 | dungeon | (17,4) | Stone wall left edge |
| `STONE_W_F` | 52 | dungeon | (18,4) | Stone wall face/front |
| `STONE_W_R` | 83 | dungeon | (19,4) | Stone wall right edge |
| `STONE_W_BL` | 84 | dungeon | (17,4) | Stone wall bottom-left (reuses left) |
| `STONE_W_B` | 85 | dungeon | (18,4) | Stone wall bottom (reuses face) |
| `STONE_W_BR` | 86 | dungeon | (19,4) | Stone wall bottom-right (reuses right) |

### Indoor Furniture

| Constant | ID | Sheet | (c,r) | Description |
|----------|----|-------|-------|-------------|
| `DESK` | 36 | indoor | (0,0) | Wooden desk |
| `CHAIR` | 37 | indoor | (5,0) | Wooden chair |
| `TABLE` | 38 | indoor | (2,3) | Conference/dining table |
| `SHELF` | 39 | indoor | (20,0) | Bookshelf |
| `PLANT_I` | 41 | indoor | (10,2) | Indoor potted plant |
| `SCROLL_OBJ` | 43 | indoor | (22,2) | Scroll on surface (YAML pickup) |

### Dungeon Props

| Constant | ID | Sheet | (c,r) | Description |
|----------|----|-------|-------|-------------|
| `PILLAR` | 54 | dungeon | (0,3) | Stone pillar/column |
| `RACK` | 56 | dungeon | (0,5) | Server rack / weapon rack |
| `TERMINAL` | 57 | dungeon | (2,5) | Computer terminal |
| `PEDESTAL` | 58 | dungeon | (8,12) | Stone pedestal (item display) |

### Item Icons (inventory UI, not placed as map tiles)

| Item | Sheet | (c,r) | Description |
|------|-------|-------|-------------|
| `rubber_duck` | base | (23,9) | Yellow rubber duck |
| `jira_ticket` | base | (20,0) | Ticket/note |
| `yaml_scroll` | base | (25,27) | Scroll icon |
| `api_key` | base | (24,27) | Key icon |
| `env_file` | base | (26,27) | File/document icon |

---

## Base Pack Region Map (`base`, 57 × 31)

### Rows 0–2: Water & Ground

```
Cols 0-2:  Water shore 3×3 tileset
           (0,0)=TL  (1,0)=T   (2,0)=TR
           (0,1)=L   (1,1)=deep (2,1)=R
           (0,2)=BL  (1,2)=B   (2,2)=BR

Cols 3-6:  Ground tiles
           (3,0)=dirt/tan  (4,0)=sand-border  (5,0)=sand    (6,0)=dark-ground
           (3,1)=grass-alt (4,1)=dirt-path     (5,1)=GRASS   (6,1)=grass-variant
           (3,2)=green-alt (4,2)=transition    (5,2)=ground  (6,2)=ground-variant
```

*Cols 7–56, rows 0–2* contain miscellaneous construction materials (planks, boards), architectural details (door frames, archways), banners, and small prop tiles. These span the full width and include hundreds of small building elements.

### Rows 3–6: Vegetation, Rocks, Props, Doors

```
Cols 7-14, rows 4-5: VEGETATION BLOCK
  (7,4)=tree-canopy   (8,4)=tree-canopy2   (9,4)=pine-canopy  (10,4)=pine-canopy2
  (7,5)=tree-trunk     (8,5)=tree-trunk2    (9,5)=pine-trunk   (10,5)=pine-trunk2
  (11,5)=bush          (12,5)=bush-variant  (13,5)=small-plant (14,5)=flower

Cols 3-6, row 6: ROCKS & STUMPS
  (3,6)=stump  (4,6)=rock  (5,6)=rock-small  (6,6)=rock-variant

Cols 27-33, row 6: DOORS
  (30,6)=exterior-door (used as DOOR_EXT)
  Nearby: other door styles, chests, crates
```

*Rows 3–6 right half (cols 15–56)* contains a dense mix of:
- Fence segments and gates (wooden, iron)
- Signs and signposts
- Gravestones, crosses, monuments
- Small treasure chests, barrels, crates
- Weapons, shields, and tool icons (cols ~33-45)
- Potions, food items, coins (cols ~45-56)

### Rows 7–19: Floor Tile Sets & Large Wall Compositions

This is the densest region — multiple terrain/floor tilesets, each in 3×3 (edge) or 4×4 (transition) grids.

**Left half (cols 0–12):**
```
Rows 7-9:    Green tile floors (emerald, forest, grass pattern variants)
Rows 10-12:  Orange/brown tile floors (brick, terra cotta, rust)
Rows 13-15:  Teal/cyan tile floors + gray stone floors
Rows 16-18:  Purple/magenta floors + tan/beige floors
Row  19:     Additional floor variants
```

Each 3×3 block provides corner/edge/center tiles for seamless terrain transitions.
Useful for: custom floor patterns in new indoor areas, courtyard tiles, arena floors.

**Right half (cols 13–45):**
```
Rows 7-12:   Beige/cream wall compositions — large multi-tile walls with
              arched windows and doorways. 3-row tall wall sections.
Rows 13-16:  Gray/blue stone wall compositions — castle/fortress style
              with arched openings and buttresses.
Rows 17-19:  Brown/wood wall compositions — timber-frame building walls.
```

These are "assembled building" regions — complete wall facades with integrated windows and doors, designed to be tiled together for large buildings. The walls are 3 rows tall (top trim, middle wall, bottom base).

**Far right (cols 46–56):**
```
Rows 7-19:   Assorted small props and decorative elements:
              - Wall-mounted torches and sconces
              - Barrels, crates, sacks
              - Armor stands, weapon racks
              - Banners and flags
              - Mining props (pickaxe, cart, ore)
              - Fence segments and railings
              - Ladders
```

### Rows 20–24: Building Exteriors (A-Frame Houses)

This is the most structured region — two complete house tile sets.

```
BEIGE HOUSE SET (cols 13-19):
  Row 21: Roof tiles    — (13,21)=peak-L  (14,21)=peak-R  (18,21)=roof-fill
                           (15,21)=roof-edge-L  (16,21)=roof-edge-R
  Row 22: Wall tiles    — (13,22)=wall-L  (14,22)=wall-R  (18,22)=wall-fill
                           (15,22)=window-L  (16,22)=window-R
                           (17,22)=wall-variant
  Row 23: Face tiles    — (13,23)=face-L  (14,23)=face-R  (18,23)=face-fill
                           (15,23)=door-L  (16,23)=door-R
                           (17,23)=face-variant
  Row 24: Foundation?   — Additional base/foundation tiles

BROWN HOUSE SET (cols 20-26):
  Row 21: Roof tiles    — (20,21)=peak-L  (21,21)=peak-R  (25,21)=roof-fill
                           (22,21)=roof-edge-L  (23,21)=roof-edge-R
  Row 22: Wall tiles    — (20,22)=wall-L  (21,22)=wall-R  (25,22)=wall-fill
                           (22,22)=door (single-tile)
                           (23,22)=wall-variant
  Row 23: Face tiles    — (20,23)=face-L  (21,23)=face-R  (25,23)=face-fill
                           (22,23)=door-alt  (23,23)=face-variant
  Row 24: Foundation?   — Additional base/foundation tiles

ADDITIONAL BUILDING VARIANTS (cols 27+, rows 20-24):
  More roof/wall/face variants in different styles — these appear to include
  gray stone and dark timber buildings. Could be used for additional
  building types if the campus grows.
```

### Rows 25–27: Items & Collectibles

```
Cols 0-10:  Weapons — swords, axes, bows, staves, daggers
Cols 11-15: Shields — various styles and colors
Cols 16-22: Accessories — rings, amulets, helmets, boots
Cols 23-27: Misc items — keys, potions, scrolls, food, gems
            (23,9)=rubber-duck  (20,0)=ticket
            (24,27)=key  (25,27)=scroll  (26,27)=document
Cols 28-35: More potions, gems, and crafting materials
Cols 36-45: UI elements and button tiles
```

### Rows 28–30: UI Elements

```
Cols 0-15:  Health/mana/XP bars — segmented bar graphics
            Multiple colors (red, green, blue, yellow, orange)
Cols 16-30: Panel frames and borders — 3×3 tilesets for UI windows
Cols 31-45: Button tiles — normal, pressed, disabled states
Cols 46-56: Additional UI elements — checkboxes, sliders, icons
```

---

## Indoor Pack Region Map (`indoor`, 27 × 18)

### Rows 0–3: Furniture

```
Row 0:  (0,0)=desk     (1,0)=desk-variant  (2,0)=table-small
        (3,0)=stool     (4,0)=bench         (5,0)=chair
        (6,0)=chair-alt (7,0)=ottoman
        Cols 8-12: More seating (stools, benches)
        Cols 13-17: Beds (single, double, colored variants)
        Cols 18-20: Wardrobes/armoires
        (20,0)=bookshelf
        Cols 21-26: Shelving, cabinets, dressers

Row 1:  Kitchen/bar furniture — counters, sinks, ovens, stoves
        Cols 0-8: Counter tops and cooking surfaces
        Cols 9-15: Appliances (stove, oven, sink, cauldron)
        Cols 16-20: Storage (barrel, crate, chest)
        Cols 21-26: More storage and display cases

Row 2:  Decorations — rugs, carpets, wall hangings, plants
        (10,2)=potted-plant  (22,2)=scroll-on-surface
        Cols 0-5: Rugs and mats
        Cols 6-9: Paintings and mirrors
        Cols 10-15: Plants, vases, candelabras
        Cols 16-20: Clocks, trophies, ornaments
        Cols 21-26: Books, papers, writing implements

Row 3:  Tables and large surfaces
        (2,3)=conference-table
        Cols 0-8: Table variants (round, rectangular, long)
        Cols 9-15: Bar/counter sections
        Cols 16-26: More large furniture
```

### Rows 4–6: Wall Tiles (3×3 tileset)

```
        Col 7    Col 8    Col 9
Row 4:  wall-TL  wall-T   wall-TR
Row 5:  wall-L   wall-F   wall-R     ← (10,5)=interior-door
Row 6:  wall-BL  wall-B   wall-BR

Additional wall styles at other column positions.
Cols 0-6: Alternative wall materials (brick, stone, plaster)
Cols 10-15: Door and window inserts for walls
Cols 16-26: More wall materials and decorative wall panels
```

### Rows 7–9: More Wall Variants & Transitions

```
Various wall transition tiles and corner pieces.
Useful for: T-junctions, crossroads in hallways, doorframe surrounds.
```

### Rows 8–12: Floor Tiles

```
(0,8)=wood-plank-floor (used as FLOOR_W)
Cols 0-5: Wood floor variants (light, dark, parquet, herringbone)
Cols 6-12: Tile floor variants (checkerboard, marble, ceramic)
Cols 13-20: Carpet/rug patterns with borders
Cols 21-26: Stone/flagstone floor variants
```

### Rows 13–17: Additional Decorations & Props

```
Rows 13-14: Musical instruments, curtains, banners
Rows 15-16: Bathroom fixtures, more kitchen items
Row 17:     Shop/store display items, signs
```

---

## Dungeon Pack Region Map (`dungeon`, 29 × 18)

### Rows 0–2: Cave & Debris

```
Cols 0-5:  Broken stone, rubble, bone piles, scattered debris
Cols 6-10: Vines, moss, mushrooms, cave flora
Cols 11-15: Stalactites/stalagmites, crystal formations
Cols 16-20: Cobwebs, chains, wall cracks
Cols 21-28: Water/lava drips, cave features
```

### Rows 3–5: Stone Walls & Dungeon Props

```
STONE WALL 3×3 TILESET:
        Col 17   Col 18   Col 19
Row 3:  wall-TL  wall-T   wall-TR
Row 4:  wall-L   wall-F   wall-R
(Same tiles reused for BL/B/BR in current code)

Props:
(0,3)=pillar    (1,3)=pillar-broken  (2,3)=pillar-variant
(0,5)=rack      (1,5)=rack-variant   (2,5)=terminal
(14,5)=cave-entrance

DARK STONE WALLS (cols 21-28, rows 3-5):
Alternative wall set — darker stone, arched doorways
Could be used for: deeper dungeon levels, crypt areas
```

### Rows 6–8: Doors, Gates, Passages

```
Cols 0-5:   Iron gates, portcullis, barred doors
Cols 6-10:  Wooden dungeon doors, reinforced doors
Cols 11-15: Passages, archways, stairways (up/down)
Cols 16-20: Trapdoors, secret passages, pit covers
Cols 21-28: More gate variants, drawbridge elements
```

### Rows 8–12: Dungeon Floor Tiles

```
(0,8)=stone-slab-floor (used as STONE_F)
Cols 0-6: Stone floor variants (cracked, mossy, bloodstained)
Cols 7-12: Brick floor variants
Cols 13-18: Sand/dirt floor with debris
(8,12)=pedestal (used as PEDESTAL)
Cols 19-28: Specialized floor tiles (magic circles, drain grates, pressure plates)
```

### Rows 12–17: Traps, Treasure, Special Objects

```
Rows 12-13: Chests (closed, open, mimic), treasure piles
Rows 14-15: Traps (spike, fire, pit), switches, levers
Rows 16-17: Altars, crystal balls, magic items, boss-room decorations
```

---

## City Pack Region Map (`city`, 37 × 28)

Currently used only for the old wall tiles (cols 8-11, rows 0-1). Most of this pack is modern/urban themed.

### Rows 0–6: Rooftops & Building Tops

```
Cols 0-7:  Flat rooftops — red, gray, brown, green (3×3 tilesets each)
Cols 8-11: GRAY WALL TILES (used for old campus buildings)
           (8,0)=wall-TL  (9,0)=wall-TR  (10,0)=wall-T
           (8,1)=wall-BL  (9,1)=wall-BR  (10,1)=wall-F
           (11,0)=wall-L  (11,1)=wall-R
Cols 12-20: More roof variants, skylights, chimneys, antennas
Cols 21-28: Building facades, windows (modern style)
Cols 29-36: Trees, bushes, hedges (city style, rounder shapes)
```

### Rows 7–14: Roads, Sidewalks, Parking

```
Cols 0-12:  Road surfaces — asphalt (gray), dirt, cobblestone
            Includes lane markings, crosswalks, intersections
Cols 13-20: Sidewalks, curbs, drainage grates
Cols 21-28: Parking lots, parking meters, benches
Cols 29-36: Fences, walls, barriers (chain-link, concrete, wood)
```

### Rows 15–20: City Props & Vehicles

```
Cols 0-10:  Street furniture — lampposts, hydrants, mailboxes,
            traffic lights, stop signs, trash cans
Cols 11-20: Building interiors — shop displays, ATMs, vending machines
Cols 21-28: Vehicles — cars, trucks, buses (top-down, 2-3 tiles each)
            Multiple colors: green, red, blue, gray
Cols 29-36: More vehicles and road objects
```

### Rows 21–27: Specialized City Tiles

```
Cols 0-12:  Ground textures — wood, brick, concrete, marble
Cols 13-20: Night/dark variants of roads and buildings
Cols 21-36: Additional building facades, neon signs, industrial
```

---

## Characters Pack Reference (`chars`, 54 × 12)

Characters are **composited from layers** drawn bottom-to-top. Each row is a character variant. Each column group is a body part category.

### Column Groups

```
Col 0:       Base body (nude skin tone)
Cols 1-2:    Body variants (different skin tones)
Col 3-5:     Pants/legs (3 styles)
Cols 6-9:    Shirt group A (4 styles, teal/green tones)
Cols 10-13:  Shirt group B (4 styles, blue/navy tones)
Cols 14-17:  Shirt group C (4 styles, pink/red/purple tones)
Cols 18:     Blank/spacer
Cols 19-22:  Hair group A (4 styles — short, medium, long, hat)
Cols 23-26:  Hair group B (4 styles — darker/alternative)
Cols 27-32:  Accessories (capes, scarves, masks)
Cols 33-38:  Shields (6 styles)
Cols 39-41:  More accessories
Cols 42-45:  Weapons — swords, staves, axes, bows
Cols 46-53:  More weapons and equipment variants
```

### Current Character Definitions

| Character | Row | Layers (col positions) | Look |
|-----------|-----|----------------------|------|
| `player` | 0 | body(0), pants(3), shirt-B(10), hair-A-hat(22), sword(42) | Teal shirt, hat, sword |
| `karen` | 1 | body(0), pants(3), shirt-C(14), hair-B-long(20) | Pink shirt, long hair |
| `merlin` | 2 | body(0), pants(3), shirt-C-robe(17), hair-A-beard(22), staff(43) | Purple robe, beard, staff |
| `datadave` | 3 | body(0), pants(3), shirt-A(6), hair-A-short(19) | Brown shirt, short hair |
| `priya` | 8 | body(0), pants(3), shirt-B(10), hair-B-long(20) | Teal shirt, long hair |
| `oracle` | 5 | body(0), pants(3), shirt-C(14), hair-B-long(20) | Dark robe, long hair |
| `steve` | 6 | body(0), pants(3), shirt-B(10), hair-B-short(23), shield(33) | Blue shirt, shield |
| `boss` | 7 | body(0), pants(3), shirt-C(14), hair-B-hat(26), big-shield(34), sword(42) | Dark armor, armed |

---

## Unused Tiles — Useful for Future Features

### Fences & Barriers (base pack)
- **Wooden fence segments**: scattered around rows 3-6, cols 15-25 — horizontal, vertical, corners, gates
- **Iron fence/railing**: similar region, darker tiles
- Could be used for: campus boundaries, garden areas, restricted zones

### Additional Tree Types (base pack)
- **(8,4)/(8,5)**: Second deciduous tree variant (different canopy shape)
- **(10,4)/(10,5)**: Second pine variant
- **(12,5)**: Alternate bush style
- **(13,5)**: Small shrub/sapling

### Path/Road Edges (base pack, rows 7-19 left)
- Multiple 3×3 tilesets for path-to-grass transitions
- Would allow smooth dirt paths with proper edges instead of hard-cut path tiles

### Treasure & Interactive Objects (dungeon pack, rows 12-15)
- Chests (closed/open), treasure piles, switches, levers
- Could be used for: loot drops, puzzle elements, secret rooms

### Stairways (dungeon pack, rows 6-8)
- Up/down stair tiles for multi-level dungeons
- Trapdoor tiles for hidden passages

### Additional Furniture (indoor pack)
- **Beds**: cols 13-17, row 0 — single and double beds
- **Kitchen**: row 1 — counters, stoves, sinks, cauldrons
- **Bathroom**: rows 15-16 — tub, toilet, sink
- **Bar/tavern**: cols 9-15, row 3 — bar counter, stools, kegs
- **Musical instruments**: row 13 — piano, harp, drums

### Signs & Markers (base pack)
- Signpost tiles around (rows 3-4, cols 15-20)
- Could be used for: directional signs, quest markers

### Modern City Elements (city pack)
- Cars, traffic lights, lampposts, vending machines
- Could be used for: humor/anachronism, Easter eggs, "parking lot" area
