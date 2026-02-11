# MVPQuest — Project Conventions

## Overview
Browser-based Zelda-like RPG parody about AI hype culture. Vanilla JS + Canvas, zero dependencies. Deployed via GitHub Pages.

## Live URL
https://scarolan.github.io/off-the-rails/mvpquest/

## File Structure
```
mvpquest/
  index.html          # Canvas, CSS, script tags
  js/
    data.js           # Tile defs, dialog, NPC roster, items, quests
    sprites.js        # Spritesheet loading, drawTile()
    engine.js         # Game loop, input, camera, state machine
    maps.js           # Map data arrays + rendering + collision
    entities.js       # Player, NPCs, enemies
    dialog.js         # Dialog box, typewriter text
    inventory.js      # Item pickup, inventory UI
    quests.js         # Quest state, flags, HUD
    audio.js          # OGG loading, pooled playback
  assets/             # Kenney roguelike tile packs + audio
```

## Technical Details
- **Canvas:** 720x480, 3x scale (16px tiles render at 48px)
- **Viewport:** 15x10 tiles
- **Spritesheets:** Kenney roguelike packs, 16x16 tiles, 1px margin, `sx = col * 17, sy = row * 17`
- **Movement:** Grid-based, 150ms cooldown, WASD/arrows
- **State machine:** title | playing | dialog | inventory | ending

## Asset Paths (from index.html)
- Base: `assets/2D assets/Roguelike Base Pack/Spritesheet/roguelikeSheet_transparent.png`
- Characters: `assets/2D assets/Roguelike Characters Pack/Spritesheet/roguelikeChar_transparent.png`
- Indoor: `assets/2D assets/Roguelike Interior Pack/Tilesheets/roguelikeIndoor_transparent.png`
- Dungeon: `assets/2D assets/Roguelike Dungeon Pack/Spritesheet/roguelikeDungeon_transparent.png`
- City: `assets/2D assets/Roguelike City Pack/Tilemap/tilemap.png`

## Spritesheet Dimensions (17px stride)
- Base: 57 cols x 31 rows
- Characters: 54 cols x 12 rows
- Indoor: 27 cols x 18 rows
- Dungeon: 29 cols x 18 rows
- City: 37 cols x 28 rows

## Testing
Open `mvpquest/index.html` in browser. No build step required.

## Git Conventions
- One commit per phase/issue
- Issues labeled `enhancement` (NOT `shelly` — added via project board later)
