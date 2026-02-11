# MVPQuest — Project Conventions

## Overview
Terminal-based (Python curses) RPG parody about AI hype culture. Single-file game, zero external dependencies. Follows shellys-arcade conventions.

## File Structure
```
mvpquest.py           # The game — all maps, dialog, NPCs, quests, engine
mvpquest_tiles.json   # Nerd Font / ASCII tileset definitions
test_mvpquest.py      # Test suite (pytest)
.github/workflows/
  shelly-label.yml    # Project board automation
```

## Technical Details
- **Engine:** Python 3 + curses, single-file (~1800 lines)
- **Terminal:** 80×24 minimum (55×20 map viewport + 23-col status panel + 3-row message bar)
- **Movement:** Grid-based, turn-based, WASD/arrows
- **State machine:** title | playing | dialog | inventory | ending
- **Tile modes:** Nerd Font (default) / ASCII — toggle with T key, persisted to ~/.mvpquest_settings
- **Tileset config:** mvpquest_tiles.json (same pattern as cyberpunk_tiles.json in shellys-arcade)

## Running
```bash
python3 mvpquest.py
```

## Controls
- WASD / Arrows: Move
- SPACE: Talk to NPC / advance dialog
- I: Inventory
- T: Toggle Nerd Font / ASCII tiles
- Q: Quit

## Testing
```bash
python3 -m pytest test_mvpquest.py -v
```

## Maps
1. **Campus** (30×25) — main overworld with buildings, pond, forest borders
2. **Office** (20×15) — Karen's office, conference room, main work area
3. **Server Room** (12×10) — server racks, Steve the sysadmin
4. **Dungeon** (25×20) — The Legacy Codebase, enemy patrols, GPT-7 boss
5. **Shrine** (9×7) — The Oracle (GPT-7)

## NPCs
Merlin (M/magenta), DataDave (D/blue), Karen (K/red), Priya (P/yellow), Oracle (O/cyan), Steve (S/white), GPT-7 Boss (G/red)

## Quest Chain
1. Welcome to HypeScale → talk to Karen
2. Get YAML Config Scroll → conference room
3. Get API Key of Power → convince Steve (need JIRA ticket from Priya)
4. Get Sacred .env File → defeat GPT-7 in dungeon
5. Ship the MVP! → return to Karen → ending sequence

## Git Conventions
- One commit per phase/issue
- Issues labeled `enhancement` (NOT `shelly` — added via project board later)

## Shelly automation pipeline
Same as shellys-arcade — issues labeled `shelly` flow through the automated pipeline.
See `.github/workflows/shelly-label.yml` for project board sync.
