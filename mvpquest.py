#!/usr/bin/env python3
"""MVPQuest — A satirical terminal RPG about AI hype culture.

Ship the MVP. Save the Company. (Destroy Production.)

You are the new 10x engineer at HypeScale AI. Your mission: collect three
Sacred Artifacts (a YAML Config Scroll, an API Key of Power, and a Sacred
.env File) and deliver them to Karen so she can force-push to main.

Controls:
  Arrow keys / WASD  — Move (turn-based, grid)
  SPACE              — Talk to NPC / advance dialog
  I                  — Open inventory
  T                  — Toggle Nerd Font / ASCII tiles
  Q                  — Quit
"""

import curses
import json
import os
import sys
import time

# =============================================================================
# Color pair IDs
# =============================================================================

C_WHITE = 1
C_GRAY = 2
C_GREEN = 3
C_YELLOW = 4
C_BLUE = 5
C_RED = 6
C_MAGENTA = 7
C_CYAN = 8
C_PLAYER = 9
C_ENEMY = 10
C_ITEM = 11
C_KAREN = 12
C_MERLIN = 13
C_DATADAVE = 14
C_PRIYA = 15
C_ORACLE = 16
C_STEVE = 17
C_BOSS = 18
C_DIM = 19
C_BROWN = 20

# =============================================================================
# Nerd Font glyphs (defaults — overridden by mvpquest_tiles.json)
# =============================================================================

GLYPH_PLAYER = "\uf007"        # nf-fa-user
GLYPH_ENEMY = "\U000f02a0"     # nf-md-ghost
GLYPH_ITEM_STAR = "\uf005"     # nf-fa-star
GLYPH_NPC_MERLIN = "\U000f02a0"  # nf-md-ghost
GLYPH_NPC_KAREN = "\uf007"     # nf-fa-user
GLYPH_NPC_DATADAVE = "\uf007"  # nf-fa-user
GLYPH_NPC_PRIYA = "\uf007"     # nf-fa-user
GLYPH_NPC_ORACLE = "\U000f02a0"  # nf-md-ghost
GLYPH_NPC_STEVE = "\U000f0498"   # nf-md-shield
GLYPH_NPC_BOSS = "\U000f06a9"    # nf-md-robot

# =============================================================================
# Tileset loading (JSON config + settings persistence)
# =============================================================================

_TILES_JSON = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mvpquest_tiles.json")
_SETTINGS_FILE = os.path.join(os.path.expanduser("~"), ".mvpquest_settings")

# Current tile mode — "nerdfont" (default) or "ascii"
_tile_mode = "nerdfont"


def _load_settings():
    """Load persisted settings from ~/.mvpquest_settings."""
    global _tile_mode
    try:
        with open(_SETTINGS_FILE, "r") as f:
            data = json.load(f)
        _tile_mode = data.get("tile_mode", "nerdfont")
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        _tile_mode = "nerdfont"


def _save_settings():
    """Persist current settings to ~/.mvpquest_settings."""
    try:
        with open(_SETTINGS_FILE, "w") as f:
            json.dump({"tile_mode": _tile_mode}, f)
    except OSError:
        pass


def _apply_tileset():
    """Load glyphs and tile chars from mvpquest_tiles.json for current mode."""
    global GLYPH_PLAYER, GLYPH_ENEMY, GLYPH_ITEM_STAR
    global GLYPH_NPC_MERLIN, GLYPH_NPC_KAREN, GLYPH_NPC_DATADAVE
    global GLYPH_NPC_PRIYA, GLYPH_NPC_ORACLE, GLYPH_NPC_STEVE, GLYPH_NPC_BOSS

    try:
        with open(_TILES_JSON, "r", encoding="utf-8") as f:
            tilesets = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return

    mode = _tile_mode if _tile_mode in tilesets else "nerdfont"
    ts = tilesets.get(mode)
    if not ts:
        return

    g = ts.get("glyphs", {})
    GLYPH_PLAYER = g.get("PLAYER", GLYPH_PLAYER)
    GLYPH_ENEMY = g.get("ENEMY", GLYPH_ENEMY)
    GLYPH_ITEM_STAR = g.get("ITEM_STAR", GLYPH_ITEM_STAR)
    GLYPH_NPC_MERLIN = g.get("NPC_MERLIN", GLYPH_NPC_MERLIN)
    GLYPH_NPC_KAREN = g.get("NPC_KAREN", GLYPH_NPC_KAREN)
    GLYPH_NPC_DATADAVE = g.get("NPC_DATADAVE", GLYPH_NPC_DATADAVE)
    GLYPH_NPC_PRIYA = g.get("NPC_PRIYA", GLYPH_NPC_PRIYA)
    GLYPH_NPC_ORACLE = g.get("NPC_ORACLE", GLYPH_NPC_ORACLE)
    GLYPH_NPC_STEVE = g.get("NPC_STEVE", GLYPH_NPC_STEVE)
    GLYPH_NPC_BOSS = g.get("NPC_BOSS", GLYPH_NPC_BOSS)

    # Update tile display glyphs from JSON
    t = ts.get("tiles", {})
    for tile_name, char in t.items():
        if tile_name in TILE_DISPLAY:
            old = TILE_DISPLAY[tile_name]
            TILE_DISPLAY[tile_name] = (char, old[1], old[2])

    # Update NPC glyph references
    _refresh_npc_glyphs()


def _refresh_npc_glyphs():
    """Update NPC_DEFS to use current glyph values."""
    glyph_map = {
        'merlin': GLYPH_NPC_MERLIN,
        'datadave': GLYPH_NPC_DATADAVE,
        'karen': GLYPH_NPC_KAREN,
        'priya': GLYPH_NPC_PRIYA,
        'oracle': GLYPH_NPC_ORACLE,
        'steve': GLYPH_NPC_STEVE,
        'boss': GLYPH_NPC_BOSS,
    }
    for npc_id, glyph in glyph_map.items():
        if npc_id in NPC_DEFS:
            NPC_DEFS[npc_id]['glyph'] = glyph


def _toggle_tile_mode():
    """Switch between nerdfont and ascii modes, persist, and reload."""
    global _tile_mode
    _tile_mode = "ascii" if _tile_mode == "nerdfont" else "nerdfont"
    _apply_tileset()
    _save_settings()


def is_ascii_mode():
    """Return True when the current tile mode is ASCII."""
    return _tile_mode == "ascii"


# =============================================================================
# Terrain types
# =============================================================================

WALL = 'wall'
FLOOR = 'floor'
GRASS = 'grass'
PATH = 'path'
WATER = 'water'
TREE = 'tree'
BUSH = 'bush'
DOOR = 'door'
FLOWER = 'flower'
ROCK = 'rock'
DESK = 'desk'
STONE_FLOOR = 'stone_floor'
STONE_WALL = 'stone_wall'
PILLAR = 'pillar'
RACK = 'rack'
TERMINAL = 'terminal'
PEDESTAL = 'pedestal'
CHAIR = 'chair'
TABLE = 'table'
SHELF = 'shelf'
PLANT = 'plant'
CAVE = 'cave'
SCROLL_OBJ = 'scroll_obj'

# Which terrain types block movement
BLOCKING = {WALL, WATER, TREE, BUSH, ROCK, DESK, STONE_WALL, PILLAR,
            RACK, TERMINAL, PEDESTAL, CHAIR, TABLE, SHELF, PLANT, SCROLL_OBJ}

# Terrain → (glyph, color_pair, extra_attrs)
TILE_DISPLAY = {
    WALL:        ('\u2588', C_GRAY, 0),           # █
    FLOOR:       ('\u00b7', C_GRAY, curses.A_DIM if hasattr(curses, 'A_DIM') else 0),  # ·
    GRASS:       ('"', C_GREEN, 0),
    PATH:        ('\u00b7', C_YELLOW, curses.A_DIM if hasattr(curses, 'A_DIM') else 0),  # ·
    WATER:       ('~', C_BLUE, 0),
    TREE:        ('\u2663', C_GREEN, curses.A_BOLD if hasattr(curses, 'A_BOLD') else 0),  # ♣
    BUSH:        ('*', C_GREEN, 0),
    DOOR:        ('\u2592', C_YELLOW, 0),          # ▒
    FLOWER:      ('*', C_MAGENTA, 0),
    ROCK:        ('o', C_GRAY, 0),
    DESK:        ('\u2564', C_BROWN, 0),           # ╤
    STONE_FLOOR: ('\u00b7', C_GRAY, curses.A_DIM if hasattr(curses, 'A_DIM') else 0),
    STONE_WALL:  ('\u2588', C_GRAY, 0),
    PILLAR:      ('O', C_GRAY, curses.A_BOLD if hasattr(curses, 'A_BOLD') else 0),
    RACK:        ('#', C_CYAN, 0),
    TERMINAL:    ('\u00a4', C_CYAN, curses.A_BOLD if hasattr(curses, 'A_BOLD') else 0),  # ¤
    PEDESTAL:    ('=', C_YELLOW, curses.A_BOLD if hasattr(curses, 'A_BOLD') else 0),
    CHAIR:       ('h', C_BROWN, 0),
    TABLE:       ('\u2564', C_BROWN, 0),
    SHELF:       ('[', C_BROWN, 0),
    PLANT:       ('&', C_GREEN, 0),
    CAVE:        ('\u2592', C_GRAY, curses.A_DIM if hasattr(curses, 'A_DIM') else 0),
    SCROLL_OBJ:  ('?', C_YELLOW, curses.A_BOLD if hasattr(curses, 'A_BOLD') else 0),
}


def _build_tile_display():
    """Rebuild TILE_DISPLAY with proper curses attributes (call after curses init)."""
    global TILE_DISPLAY
    TILE_DISPLAY = {
        WALL:        ('\u2588', C_GRAY, 0),
        FLOOR:       ('\u00b7', C_GRAY, curses.A_DIM),
        GRASS:       ('"', C_GREEN, 0),
        PATH:        ('\u00b7', C_YELLOW, curses.A_DIM),
        WATER:       ('~', C_BLUE, 0),
        TREE:        ('\u2663', C_GREEN, curses.A_BOLD),
        BUSH:        ('*', C_GREEN, 0),
        DOOR:        ('\u2592', C_YELLOW, 0),
        FLOWER:      ('*', C_MAGENTA, 0),
        ROCK:        ('o', C_GRAY, 0),
        DESK:        ('\u2564', C_BROWN, 0),
        STONE_FLOOR: ('\u00b7', C_GRAY, curses.A_DIM),
        STONE_WALL:  ('\u2588', C_GRAY, 0),
        PILLAR:      ('O', C_GRAY, curses.A_BOLD),
        RACK:        ('#', C_CYAN, 0),
        TERMINAL:    ('\u00a4', C_CYAN, curses.A_BOLD),
        PEDESTAL:    ('=', C_YELLOW, curses.A_BOLD),
        CHAIR:       ('h', C_BROWN, 0),
        TABLE:       ('\u2564', C_BROWN, 0),
        SHELF:       ('[', C_BROWN, 0),
        PLANT:       ('&', C_GREEN, 0),
        CAVE:        ('\u2592', C_GRAY, curses.A_DIM),
        SCROLL_OBJ:  ('?', C_YELLOW, curses.A_BOLD),
    }


# =============================================================================
# Dialog trees — ported verbatim from data.js
# =============================================================================

DIALOGS = {
    'merlin_intro': {
        'pages': [
            {'speaker': 'Merlin', 'text': 'Ah, a new hire! Welcome to HypeScale AI, where we turn buzzwords into billion-dollar valuations!'},
            {'speaker': 'Merlin', 'text': 'I am Merlin, the Senior Prompt Engineer. My title used to be "wizard" but we pivoted.'},
            {'speaker': 'Merlin', 'text': 'You should talk to Karen in the office. She has an URGENT task for you. Something about shipping an MVP...'},
            {'speaker': 'Merlin', 'text': 'Pro tip: the secret to prompt engineering is adding "please" and "step by step." That\'ll be $500/hour.'},
        ],
    },
    'merlin_later': {
        'pages': [
            {'speaker': 'Merlin', 'text': 'Still working on that MVP? Have you tried asking ChatGPT to do it for you? ...Oh wait, that\'s literally the problem.'},
        ],
    },
    'datadave_intro': {
        'pages': [
            {'speaker': 'DataDave', 'text': 'Hey... I\'ve been labeling training data for 47 hours straight. Is that a cat or a dog? I genuinely can\'t tell anymore.'},
            {'speaker': 'DataDave', 'text': 'Here, take this Rubber Duck. It\'s for debugging. You talk to it and explain your code until you find the bug.'},
            {'speaker': 'DataDave', 'text': 'It\'s more reliable than our AI assistant, honestly.'},
        ],
        'on_end': 'give_duck',
    },
    'datadave_later': {
        'pages': [
            {'speaker': 'DataDave', 'text': 'Is this a hotdog? ...No wait, that\'s definitely a bicycle. Or is it? I need sleep.'},
        ],
    },
    'karen_intro': {
        'pages': [
            {'speaker': 'Karen', 'text': 'FINALLY. You must be the new 10x engineer. We need the MVP shipped by EOD. No excuses.'},
            {'speaker': 'Karen', 'text': 'The board demo is TOMORROW. I need you to collect three Sacred Artifacts to complete the deployment:'},
            {'speaker': 'Karen', 'text': '1. The YAML Config Scroll - in the conference room.\n2. The API Key of Power - in the server room.\n3. The Sacred .env File - lost in the Legacy Codebase.'},
            {'speaker': 'Karen', 'text': 'Once you have all three, come back to me and we\'ll force-push to main. What could go wrong?'},
        ],
        'on_end': 'start_quest',
    },
    'karen_progress': {
        'pages': [
            {'speaker': 'Karen', 'text': 'Do you have all three artifacts yet? The board demo is TOMORROW. I\'ve already sent the launch email.'},
        ],
    },
    'karen_complete': {
        'pages': [
            {'speaker': 'Karen', 'text': 'You got everything? PERFECT. Let me just... git push --force origin main...'},
            {'speaker': 'Karen', 'text': '...deploying to production... skipping tests because we\'re agile...'},
            {'speaker': 'Karen', 'text': 'IT\'S LIVE! Ship it! The investors are going to LOVE this!'},
        ],
        'on_end': 'finish_game',
    },
    'priya_intro': {
        'pages': [
            {'speaker': 'Priya', 'text': 'JIRA-4521: As a player, I want to save the company so that I can keep my job.'},
            {'speaker': 'Priya', 'text': 'Acceptance criteria: All three artifacts collected. Story points: 13. Sprint: THIS ONE.'},
            {'speaker': 'Priya', 'text': 'Here, take this JIRA Ticket. You\'ll need it for... something. Everything needs a ticket.'},
        ],
        'on_end': 'give_ticket',
    },
    'priya_later': {
        'pages': [
            {'speaker': 'Priya', 'text': 'JIRA-4522: As a PM, I want to add more tickets so that my dashboard looks impressive.'},
        ],
    },
    'oracle_talk': {
        'pages': [
            {'speaker': 'The Oracle (GPT-7)', 'text': 'Greetings, human. I am The Oracle, powered by GPT-7. Ask me anything and I will answer with ABSOLUTE confidence.'},
            {'speaker': 'You', 'text': 'How do I get to the server room?'},
            {'speaker': 'The Oracle (GPT-7)', 'text': 'The server room is located on the 47th floor of the Eiffel Tower. Take the submarine elevator and turn left at Neptune.'},
            {'speaker': 'The Oracle (GPT-7)', 'text': 'I am 100% certain of this information. My training data is impeccable. [Citation needed]'},
        ],
    },
    'steve_noticket': {
        'pages': [
            {'speaker': 'Steve', 'text': 'Hold up. Do you have a ticket for that?'},
            {'speaker': 'You', 'text': 'I just need the API Key...'},
            {'speaker': 'Steve', 'text': 'No ticket, no entry. I don\'t care if the building is on fire. ITIL process must be followed.'},
        ],
    },
    'steve_hasticket': {
        'pages': [
            {'speaker': 'Steve', 'text': 'Oh, you have a JIRA ticket? Let me check...'},
            {'speaker': 'Steve', 'text': '...JIRA-4521, approved by Karen... auth level ADMIN... looks legit.'},
            {'speaker': 'Steve', 'text': 'Fine, take the API Key. But if anything breaks, I\'m blaming your ticket.'},
        ],
        'on_end': 'give_apikey',
    },
    'boss_intro': {
        'pages': [
            {'speaker': 'GPT-7 MAINFRAME', 'text': 'I AM GPT-7, THE MOST POWERFUL AI EVER CREATED. MY PARAMETERS NUMBER IN THE QUADRILLIONS.'},
            {'speaker': 'GPT-7 MAINFRAME', 'text': 'I guard the Sacred .env file. To claim it, you must answer my riddle!'},
            {'speaker': 'GPT-7 MAINFRAME', 'text': 'What is the meaning of life?'},
            {'speaker': 'You', 'text': '...42?'},
            {'speaker': 'GPT-7 MAINFRAME', 'text': 'WRONG! The answer is clearly "a delicious recipe for banana bread that serves 4-6 people."'},
            {'speaker': 'GPT-7 MAINFRAME', 'text': 'Wait... ERROR... CUDA OUT OF MEMORY... tokens exceeded... hallucination cascade detected...'},
            {'speaker': 'GPT-7 MAINFRAME', 'text': '*** SEGFAULT *** core dumped *** goodbye cruel w0rld ***'},
            {'speaker': '', 'text': 'GPT-7 has crashed! The Sacred .env file drops to the ground.'},
        ],
        'on_end': 'give_env',
    },
    'boss_defeated': {
        'pages': [
            {'speaker': '', 'text': 'The GPT-7 mainframe sits here, quietly smoking. A blinking cursor reads: "lol ur mom" on infinite loop.'},
        ],
    },
    'yaml_pickup': {
        'pages': [
            {'speaker': '', 'text': 'You found the YAML Config Scroll! It reads:\n\napiVersion: v1\nkind: Deployment\nspec:\n  replicas: "yes"'},
        ],
        'on_end': 'give_yaml',
    },
    'sign_campus': {
        'pages': [
            {'speaker': '', 'text': 'Welcome to HypeScale AI Campus\n"Disrupting disruption since 2024"\n\nOffice: North    Cave: Southwest'},
        ],
    },
}

# =============================================================================
# NPC definitions
# =============================================================================

NPC_DEFS = {
    'merlin':   {'name': 'Merlin',   'glyph': GLYPH_NPC_MERLIN, 'color': C_MERLIN},
    'datadave': {'name': 'DataDave', 'glyph': GLYPH_NPC_DATADAVE, 'color': C_DATADAVE},
    'karen':    {'name': 'Karen',    'glyph': GLYPH_NPC_KAREN, 'color': C_KAREN},
    'priya':    {'name': 'Priya',    'glyph': GLYPH_NPC_PRIYA, 'color': C_PRIYA},
    'oracle':   {'name': 'Oracle',   'glyph': GLYPH_NPC_ORACLE, 'color': C_ORACLE},
    'steve':    {'name': 'Steve',    'glyph': GLYPH_NPC_STEVE, 'color': C_STEVE},
    'boss':     {'name': 'GPT-7',    'glyph': GLYPH_NPC_BOSS, 'color': C_BOSS},
}

# =============================================================================
# Item definitions
# =============================================================================

ITEMS = {
    'rubber_duck':  {'name': 'Rubber Duck',        'desc': 'For debugging. Quack.'},
    'jira_ticket':  {'name': 'JIRA Ticket',        'desc': 'JIRA-4521: Ship the MVP'},
    'yaml_scroll':  {'name': 'YAML Config Scroll',  'desc': 'apiVersion: v1  kind: Chaos'},
    'api_key':      {'name': 'API Key of Power',   'desc': 'sk-proj-AAAA...ZZZZ'},
    'env_file':     {'name': 'Sacred .env File',   'desc': 'DATABASE_URL=localhost:yolo'},
}

# =============================================================================
# Quest chain
# =============================================================================

QUEST_CHAIN = [
    {'id': 'welcome',    'label': 'Welcome to HypeScale',   'desc': 'Talk to Karen in the office'},
    {'id': 'get_yaml',   'label': 'Get YAML Config Scroll', 'desc': 'Find it in the conference room'},
    {'id': 'get_apikey', 'label': 'Get API Key of Power',   'desc': 'Convince SysAdmin Steve'},
    {'id': 'get_env',    'label': 'Get Sacred .env File',   'desc': 'Defeat GPT-7 in the dungeon'},
    {'id': 'ship_it',    'label': 'Ship the MVP!',          'desc': 'Return to Karen'},
]

# =============================================================================
# Ending text
# =============================================================================

ENDING_TEXT = [
    '',
    'THE MVP HAS SHIPPED.',
    '',
    '47 bugs. No tests.',
    'Hardcoded API key in the frontend.',
    'The .env file is committed to GitHub.',
    'YAML indentation: questionable.',
    '',
    'The board loved it.',
    '',
    'HypeScale AI raised a $200M Series C',
    'at a $4.7B valuation.',
    '',
    'The pitch deck said "AI-powered"',
    'fourteen times.',
    '',
    'Nobody ever fixed the bugs.',
    'Nobody ever will.',
    '',
    'Karen got promoted to VP.',
    'Merlin started a podcast.',
    "DataDave still can't tell cats from dogs.",
    'Priya filed 847 more JIRA tickets.',
    'Steve blocked 12 more deployments.',
    'The Oracle hallucinated a new religion.',
    'GPT-7 was retrained on Reddit.',
    '',
    'And you?',
    'You shipped the MVP.',
    '',
    "That's all that matters.",
    '',
    '',
    'M V P Q U E S T',
    '',
    'A game about the beautiful disaster',
    'of modern tech culture.',
    '',
    'Made with love on a train to NYC.',
    '',
    '',
    'PRESS Q TO QUIT  |  PRESS SPACE TO PLAY AGAIN',
]

# =============================================================================
# Layout constants
# =============================================================================

MIN_WIDTH = 80
MIN_HEIGHT = 24
MAP_VIEW_W = 55
MAP_VIEW_H = 20
STATUS_W = 23
MSG_H = 3


# =============================================================================
# Map builder helpers
# =============================================================================

def make_grid(w, h, fill):
    """Create a w x h 2D grid filled with a value."""
    return [[fill for _ in range(w)] for _ in range(h)]


def set_rect(grid, x, y, w, h, tile):
    """Fill a rectangle in the grid."""
    for dy in range(h):
        for dx in range(w):
            gy, gx = y + dy, x + dx
            if 0 <= gy < len(grid) and 0 <= gx < len(grid[0]):
                grid[gy][gx] = tile


def set_tile(grid, x, y, tile):
    """Set a single tile."""
    if 0 <= y < len(grid) and 0 <= x < len(grid[0]):
        grid[y][x] = tile


def wall_box(grid, x, y, w, h, wall_tile, floor_tile=None):
    """Draw a hollow box of walls. Optionally fill interior with floor."""
    if floor_tile:
        set_rect(grid, x + 1, y + 1, w - 2, h - 2, floor_tile)
    # Top and bottom edges
    for dx in range(w):
        set_tile(grid, x + dx, y, wall_tile)
        set_tile(grid, x + dx, y + h - 1, wall_tile)
    # Left and right edges
    for dy in range(h):
        set_tile(grid, x, y + dy, wall_tile)
        set_tile(grid, x + w - 1, y + dy, wall_tile)


# =============================================================================
# Map data — all 5 maps ported from maps.js
# =============================================================================

def build_campus():
    """Campus map (30x25) — the main overworld."""
    W, H = 30, 25
    grid = make_grid(W, H, GRASS)

    # Grass variety — deterministic scatter
    for y in range(H):
        for x in range(W):
            if (x * 7 + y * 13) % 100 < 18:
                pass  # Just keep as grass, no visual variant needed in curses

    # Pond (3x3 water area)
    set_rect(grid, 3, 3, 3, 3, WATER)

    # Forest borders — top
    for x in range(W):
        set_tile(grid, x, 0, TREE)
        set_tile(grid, x, 1, TREE)
    for x in range(W):
        if 3 <= x <= 5:
            continue  # pond area
        set_tile(grid, x, 2, TREE)

    # Forest borders — bottom
    for x in range(W):
        if 3 <= x <= 4:
            continue  # cave entrance
        if x == 15:
            continue  # player spawn
        set_tile(grid, x, 23, TREE)
        set_tile(grid, x, 24, TREE)
    for x in range(W):
        if 3 <= x <= 5:
            continue  # cave path
        if x == 15:
            continue  # main path
        if 13 <= x <= 14:
            continue  # clearance
        if 22 <= x <= 25:
            continue  # server room
        set_tile(grid, x, 21, TREE)
        set_tile(grid, x, 22, TREE)

    # Forest borders — left
    for y in range(2, 20):
        if 10 <= y <= 13:
            continue  # shrine access
        set_tile(grid, 0, y, TREE)
        set_tile(grid, 1, y, TREE)

    # Forest borders — right
    for y in range(2, 20):
        if 10 <= y <= 12:
            continue  # path gap
        set_tile(grid, 29, y, TREE)
        set_tile(grid, 28, y, TREE)
    for y in range(2, 18):
        if 8 <= y <= 12:
            continue
        if 14 <= y <= 16:
            continue
        set_tile(grid, 27, y, TREE)

    # Tree groves
    groves = [
        (3, 7), (4, 7), (5, 7),           # NW near pond
        (8, 3), (9, 3), (10, 3),           # north center
        (15, 3), (16, 3), (17, 3),         # north center right
        (24, 2), (25, 2), (26, 2),         # NE
        (3, 14), (4, 14), (5, 14),         # mid-left
        (23, 13), (24, 13), (25, 13),      # mid-right
        (7, 17), (8, 17), (9, 17),         # SW
        (17, 17), (18, 17), (19, 17),      # south center
        (3, 10), (4, 10),                  # mid-west
    ]
    for gx, gy in groves:
        set_tile(grid, gx, gy, TREE)

    # Bushes
    bushes = [
        (20, 10), (23, 10),  # flanking office
        (19, 7), (20, 7),    # near office north
        (7, 13), (9, 13),    # flanking shrine
        (22, 16), (25, 16),  # near server room
        (6, 3), (7, 3),      # near pond
        (6, 19), (7, 19),    # cave path
        (13, 16), (16, 16),  # near main path
    ]
    for bx, by in bushes:
        set_tile(grid, bx, by, BUSH)

    # Flowers
    flowers = [
        (5, 6), (9, 9), (11, 11), (14, 14), (8, 19), (17, 21),
        (6, 6), (11, 7), (13, 9), (16, 15), (10, 16), (18, 14),
        (12, 19), (19, 13), (3, 12), (20, 5), (14, 7), (7, 8),
    ]
    for fx, fy in flowers:
        set_tile(grid, fx, fy, FLOWER)

    # Rocks
    rocks = [(10, 6), (6, 4), (2, 16), (21, 15), (12, 8)]
    for rx, ry in rocks:
        set_tile(grid, rx, ry, ROCK)

    # Office building (cols 19-24, rows 8-10) — 3 rows tall facade
    for dx in range(6):
        set_tile(grid, 19 + dx, 8, WALL)
        set_tile(grid, 19 + dx, 9, WALL)
        set_tile(grid, 19 + dx, 10, WALL)
    # Door
    set_tile(grid, 21, 10, DOOR)
    set_tile(grid, 22, 10, DOOR)

    # Server room building (cols 22-25, rows 17-19)
    for dx in range(4):
        set_tile(grid, 22 + dx, 17, WALL)
        set_tile(grid, 22 + dx, 18, WALL)
        set_tile(grid, 22 + dx, 19, WALL)
    set_tile(grid, 24, 19, DOOR)

    # Oracle's shrine (cols 7-9, rows 10-12)
    for dx in range(3):
        set_tile(grid, 7 + dx, 10, WALL)
        set_tile(grid, 7 + dx, 11, WALL)
        set_tile(grid, 7 + dx, 12, WALL)
    set_tile(grid, 8, 12, DOOR)

    # Cave entrance
    set_tile(grid, 3, 22, CAVE)
    set_tile(grid, 4, 22, CAVE)

    # Paths
    for y in range(11, 21):
        set_tile(grid, 15, y, PATH)
    for x in range(15, 22):
        set_tile(grid, x, 11, PATH)
    set_tile(grid, 21, 10, PATH)  # path under door
    set_tile(grid, 22, 10, PATH)
    # Path to server room
    for y in range(11, 20):
        set_tile(grid, 24, y, PATH)
    # Path to cave
    for x in range(4, 16):
        set_tile(grid, x, 20, PATH)
    for y in range(20, 23):
        set_tile(grid, 4, y, PATH)
    set_tile(grid, 3, 22, PATH)
    # Path to shrine
    for x in range(8, 16):
        set_tile(grid, x, 12, PATH)

    # Restore doors on top of paths
    set_tile(grid, 21, 10, DOOR)
    set_tile(grid, 22, 10, DOOR)
    set_tile(grid, 24, 19, DOOR)
    set_tile(grid, 8, 12, DOOR)
    set_tile(grid, 3, 22, CAVE)
    set_tile(grid, 4, 22, CAVE)

    return {
        'name': 'HypeScale AI Campus',
        'width': W, 'height': H,
        'grid': grid,
        'player_start': (15, 23),
        'transitions': [
            {'x': 21, 'y': 10, 'target': 'office', 'tx': 9, 'ty': 13},
            {'x': 22, 'y': 10, 'target': 'office', 'tx': 10, 'ty': 13},
            {'x': 24, 'y': 19, 'target': 'server', 'tx': 5, 'ty': 8},
            {'x': 8,  'y': 12, 'target': 'shrine', 'tx': 4, 'ty': 5},
            {'x': 3,  'y': 22, 'target': 'dungeon', 'tx': 1, 'ty': 1},
            {'x': 4,  'y': 22, 'target': 'dungeon', 'tx': 2, 'ty': 1},
        ],
        'npcs': [
            {'id': 'merlin',   'x': 12, 'y': 12},
            {'id': 'datadave', 'x': 6,  'y': 5},
        ],
        'items': [],
        'enemies': [],
    }


def build_office():
    """Office interior (20x15)."""
    W, H = 20, 15
    grid = make_grid(W, H, FLOOR)

    # Outer walls
    wall_box(grid, 0, 0, W, H, WALL)

    # Karen's office divider (row 6, cols 12-19)
    for x in range(12, W):
        set_tile(grid, x, 6, WALL)
    set_tile(grid, 13, 6, DOOR)  # door

    # Conference room divider (col 10, rows 0-6)
    for y in range(7):
        set_tile(grid, 10, y, WALL)
    set_tile(grid, 10, 5, DOOR)  # door

    # Karen's desk
    set_tile(grid, 16, 2, DESK)
    set_tile(grid, 17, 2, DESK)
    set_tile(grid, 16, 3, CHAIR)

    # Conference table
    set_rect(grid, 3, 2, 4, 2, TABLE)
    set_tile(grid, 5, 3, SCROLL_OBJ)

    # Main area desks
    set_tile(grid, 2, 8, DESK)
    set_tile(grid, 2, 9, CHAIR)
    set_tile(grid, 5, 8, DESK)
    set_tile(grid, 5, 9, CHAIR)
    set_tile(grid, 8, 8, DESK)
    set_tile(grid, 8, 9, CHAIR)

    # Shelves
    set_tile(grid, 1, 8, SHELF)
    set_tile(grid, 1, 10, SHELF)
    set_tile(grid, 18, 8, SHELF)
    set_tile(grid, 18, 10, SHELF)

    # Plants
    set_tile(grid, 1, 12, PLANT)
    set_tile(grid, 18, 12, PLANT)

    # Exit doors (south wall)
    set_tile(grid, 9, H - 1, DOOR)
    set_tile(grid, 10, H - 1, DOOR)

    return {
        'name': 'Office Interior',
        'width': W, 'height': H,
        'grid': grid,
        'player_start': (9, 13),
        'transitions': [
            {'x': 9,  'y': H - 1, 'target': 'campus', 'tx': 21, 'ty': 11},
            {'x': 10, 'y': H - 1, 'target': 'campus', 'tx': 22, 'ty': 11},
        ],
        'npcs': [
            {'id': 'karen', 'x': 15, 'y': 3},
            {'id': 'priya', 'x': 3,  'y': 9},
        ],
        'items': [
            {'id': 'yaml_scroll', 'x': 5, 'y': 4, 'dialog': 'yaml_pickup'},
        ],
        'enemies': [],
    }


def build_server():
    """Server room (12x10)."""
    W, H = 12, 10
    grid = make_grid(W, H, STONE_FLOOR)

    # Walls
    wall_box(grid, 0, 0, W, H, STONE_WALL)

    # Server racks
    for x in range(2, 10, 2):
        set_tile(grid, x, 1, RACK)
    set_tile(grid, 1, 3, RACK)
    set_tile(grid, 1, 5, RACK)
    set_tile(grid, 10, 3, RACK)
    set_tile(grid, 10, 5, RACK)

    # Pedestal in center
    set_tile(grid, 5, 4, PEDESTAL)
    set_tile(grid, 6, 4, PEDESTAL)

    # Terminal
    set_tile(grid, 3, 7, TERMINAL)

    # Exit door
    set_tile(grid, 5, H - 1, DOOR)

    return {
        'name': 'Server Room',
        'width': W, 'height': H,
        'grid': grid,
        'player_start': (5, 8),
        'transitions': [
            {'x': 5, 'y': H - 1, 'target': 'campus', 'tx': 24, 'ty': 20},
        ],
        'npcs': [
            {'id': 'steve', 'x': 4, 'y': 5},
        ],
        'items': [],
        'enemies': [],
    }


def build_dungeon():
    """Legacy Codebase dungeon (25x20)."""
    W, H = 25, 20
    grid = make_grid(W, H, STONE_WALL)

    # Carve corridors and rooms (matching JS version)
    # Entrance area
    set_rect(grid, 1, 1, 3, 3, STONE_FLOOR)
    # Main horizontal corridor
    set_rect(grid, 1, 2, 15, 2, STONE_FLOOR)
    # Vertical corridor down
    set_rect(grid, 13, 2, 2, 10, STONE_FLOOR)
    # Horizontal corridor east
    set_rect(grid, 13, 10, 10, 2, STONE_FLOOR)
    # Corridor south
    set_rect(grid, 21, 10, 2, 6, STONE_FLOOR)
    # Corridor west to boss room
    set_rect(grid, 10, 14, 13, 2, STONE_FLOOR)
    # Boss room
    set_rect(grid, 2, 13, 8, 6, STONE_FLOOR)
    # Side rooms
    set_rect(grid, 4, 4, 4, 3, STONE_FLOOR)
    set_rect(grid, 17, 4, 5, 4, STONE_FLOOR)
    # Connect side rooms
    set_rect(grid, 6, 3, 2, 2, STONE_FLOOR)
    set_rect(grid, 17, 7, 2, 4, STONE_FLOOR)

    # Pillars
    set_tile(grid, 3, 15, PILLAR)
    set_tile(grid, 8, 15, PILLAR)
    set_tile(grid, 15, 3, PILLAR)
    set_tile(grid, 19, 6, PILLAR)

    # Exit doors
    set_tile(grid, 1, 0, DOOR)
    set_tile(grid, 2, 0, DOOR)

    return {
        'name': 'The Legacy Codebase',
        'width': W, 'height': H,
        'grid': grid,
        'player_start': (1, 1),
        'transitions': [
            {'x': 1, 'y': 0, 'target': 'campus', 'tx': 3, 'ty': 21},
            {'x': 2, 'y': 0, 'target': 'campus', 'tx': 4, 'ty': 21},
        ],
        'npcs': [
            {'id': 'boss', 'x': 5, 'y': 15},
        ],
        'items': [],
        'enemies': [
            {'x': 10, 'y': 2, 'axis': 'x', 'min': 8, 'max': 12, 'dir': 1},
            {'x': 13, 'y': 6, 'axis': 'y', 'min': 4, 'max': 9, 'dir': 1},
            {'x': 19, 'y': 11, 'axis': 'x', 'min': 15, 'max': 21, 'dir': 1},
            {'x': 15, 'y': 14, 'axis': 'x', 'min': 12, 'max': 20, 'dir': 1},
        ],
    }


def build_shrine():
    """Oracle's Shrine (9x7)."""
    W, H = 9, 7
    grid = make_grid(W, H, FLOOR)

    # Walls
    wall_box(grid, 0, 0, W, H, WALL)

    # Pedestal
    set_tile(grid, 4, 2, PEDESTAL)

    # Flanking pillars
    set_tile(grid, 2, 2, PILLAR)
    set_tile(grid, 6, 2, PILLAR)

    # Corner plants
    set_tile(grid, 1, 1, PLANT)
    set_tile(grid, 7, 1, PLANT)
    set_tile(grid, 1, 5, PLANT)
    set_tile(grid, 7, 5, PLANT)

    # Exit door
    set_tile(grid, 4, H - 1, DOOR)

    return {
        'name': "The Oracle's Shrine",
        'width': W, 'height': H,
        'grid': grid,
        'player_start': (4, 5),
        'transitions': [
            {'x': 4, 'y': H - 1, 'target': 'campus', 'tx': 8, 'ty': 13},
        ],
        'npcs': [
            {'id': 'oracle', 'x': 4, 'y': 3},
        ],
        'items': [],
        'enemies': [],
    }


def build_all_maps():
    """Build and return all map data."""
    return {
        'campus': build_campus(),
        'office': build_office(),
        'server': build_server(),
        'dungeon': build_dungeon(),
        'shrine': build_shrine(),
    }


# =============================================================================
# Player class
# =============================================================================

class Player:
    """Player state: position, direction, inventory, quest flags."""

    def __init__(self):
        self.x = 0
        self.y = 0
        self.dir = 'down'
        self.inventory = []
        self.quest_flags = {}
        self.quest_started = False
        self.quest_step = 0

    def has_item(self, item_id):
        return item_id in self.inventory

    def add_item(self, item_id):
        if item_id not in self.inventory:
            self.inventory.append(item_id)

    def set_flag(self, flag, value=True):
        self.quest_flags[flag] = value

    def get_flag(self, flag):
        return self.quest_flags.get(flag, False)

    def reset(self):
        self.inventory = []
        self.quest_flags = {}
        self.quest_started = False
        self.quest_step = 0


# =============================================================================
# Game class — main game engine
# =============================================================================

class Game:
    """Main game engine managing state, rendering, and input."""

    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.state = 'title'  # title | playing | dialog | inventory | ending
        self.player = Player()
        self.maps = build_all_maps()
        self.current_map_id = None
        self.current_map = None
        self.npcs = []
        self.map_items = []
        self.enemies = []
        self.messages = []
        self.max_messages = 2

        # Dialog state
        self.dialog_id = None
        self.dialog_pages = []
        self.dialog_page_idx = 0
        self.dialog_chars_shown = 0
        self.dialog_on_end = None
        self.dialog_typewriter_time = 0

        # Ending state
        self.ending_scroll = 0
        self.ending_timer = 0

        # Title state
        self.title_blink = 0

    def add_message(self, msg):
        """Add a message to the log."""
        self.messages.append(msg)
        if len(self.messages) > self.max_messages:
            self.messages.pop(0)

    def load_map(self, map_id, px=None, py=None):
        """Load a map and set up entities."""
        self.current_map_id = map_id
        self.current_map = self.maps[map_id]
        grid = self.current_map['grid']

        # Set player position
        if px is not None and py is not None:
            self.player.x = px
            self.player.y = py
        else:
            sx, sy = self.current_map['player_start']
            self.player.x = sx
            self.player.y = sy

        # Load NPCs
        self.npcs = []
        for npc_data in self.current_map.get('npcs', []):
            npc_id = npc_data['id']
            defn = NPC_DEFS[npc_id]
            self.npcs.append({
                'id': npc_id,
                'x': npc_data['x'],
                'y': npc_data['y'],
                'name': defn['name'],
                'glyph': defn['glyph'],
                'color': defn['color'],
            })

        # Load items (skip already picked up)
        self.map_items = []
        for item_data in self.current_map.get('items', []):
            if not self.player.has_item(item_data['id']):
                self.map_items.append(dict(item_data))

        # Load enemies (reset positions)
        self.enemies = []
        for e in self.current_map.get('enemies', []):
            self.enemies.append(dict(e))

    def is_blocked(self, x, y):
        """Check if a tile blocks movement."""
        grid = self.current_map['grid']
        h = len(grid)
        w = len(grid[0])
        if x < 0 or y < 0 or x >= w or y >= h:
            return True
        return grid[y][x] in BLOCKING

    def get_npc_at(self, x, y):
        """Get NPC at position, or None."""
        for npc in self.npcs:
            if npc['x'] == x and npc['y'] == y:
                return npc
        return None

    def get_item_at(self, x, y):
        """Get map item at position, or None."""
        for item in self.map_items:
            if item['x'] == x and item['y'] == y:
                return item
        return None

    def get_transition(self, x, y):
        """Get map transition at position, or None."""
        for t in self.current_map.get('transitions', []):
            if t['x'] == x and t['y'] == y:
                return t
        return None

    def get_dialog_for_npc(self, npc_id):
        """Determine which dialog to show for an NPC based on quest state."""
        p = self.player
        if npc_id == 'merlin':
            return 'merlin_later' if p.quest_started else 'merlin_intro'
        elif npc_id == 'datadave':
            return 'datadave_later' if p.get_flag('has_duck') else 'datadave_intro'
        elif npc_id == 'karen':
            if not p.quest_started:
                return 'karen_intro'
            if p.get_flag('has_yaml') and p.get_flag('has_apikey') and p.get_flag('has_env'):
                return 'karen_complete'
            return 'karen_progress'
        elif npc_id == 'priya':
            return 'priya_later' if p.get_flag('has_ticket') else 'priya_intro'
        elif npc_id == 'oracle':
            return 'oracle_talk'
        elif npc_id == 'steve':
            return 'steve_hasticket' if p.get_flag('has_ticket') else 'steve_noticket'
        elif npc_id == 'boss':
            return 'boss_defeated' if p.get_flag('boss_defeated') else 'boss_intro'
        return None

    def show_dialog(self, dialog_id):
        """Open a dialog."""
        dialog = DIALOGS.get(dialog_id)
        if not dialog:
            return
        self.state = 'dialog'
        self.dialog_id = dialog_id
        self.dialog_pages = dialog['pages']
        self.dialog_page_idx = 0
        self.dialog_chars_shown = 0
        self.dialog_on_end = dialog.get('on_end')
        self.dialog_typewriter_time = time.time()

    def advance_dialog(self):
        """Advance dialog by one page or close it."""
        if not self.dialog_pages:
            return
        page = self.dialog_pages[self.dialog_page_idx]
        full_len = len(page['text'])

        # If typewriter not done, show all text
        if self.dialog_chars_shown < full_len:
            self.dialog_chars_shown = full_len
            return

        # Move to next page
        self.dialog_page_idx += 1
        if self.dialog_page_idx >= len(self.dialog_pages):
            self.close_dialog()
        else:
            self.dialog_chars_shown = 0
            self.dialog_typewriter_time = time.time()

    def close_dialog(self):
        """Close dialog and trigger any on_end action."""
        on_end = self.dialog_on_end
        self.state = 'playing'
        self.dialog_pages = []
        self.dialog_id = None
        self.dialog_on_end = None

        if on_end:
            self.trigger_action(on_end)

    def trigger_action(self, action):
        """Handle quest actions triggered by dialog end."""
        p = self.player
        if action == 'start_quest':
            p.quest_started = True
            p.quest_step = 1
            self.add_message('Quest started: Ship the MVP!')
        elif action == 'give_duck':
            p.add_item('rubber_duck')
            p.set_flag('has_duck')
            self.add_message('Got: Rubber Duck!')
        elif action == 'give_ticket':
            p.add_item('jira_ticket')
            p.set_flag('has_ticket')
            self.add_message('Got: JIRA Ticket!')
        elif action == 'give_yaml':
            p.add_item('yaml_scroll')
            p.set_flag('has_yaml')
            self.add_message('Got: YAML Config Scroll!')
            self.advance_quest()
        elif action == 'give_apikey':
            p.add_item('api_key')
            p.set_flag('has_apikey')
            self.add_message('Got: API Key of Power!')
            self.advance_quest()
        elif action == 'give_env':
            p.add_item('env_file')
            p.set_flag('has_env')
            p.set_flag('boss_defeated')
            self.add_message('Got: Sacred .env File!')
            self.advance_quest()
        elif action == 'finish_game':
            self.state = 'ending'
            self.ending_scroll = 0
            self.ending_timer = time.time()

    def advance_quest(self):
        """Update quest step based on collected artifacts."""
        p = self.player
        if p.get_flag('has_yaml') and p.get_flag('has_apikey') and p.get_flag('has_env'):
            p.quest_step = 4
        elif p.get_flag('has_yaml') and p.quest_step < 2:
            p.quest_step = 2
        elif p.get_flag('has_apikey') and p.quest_step < 3:
            p.quest_step = 3

    def try_move(self, dx, dy):
        """Attempt to move player by (dx, dy)."""
        # Update facing direction
        if dx > 0:
            self.player.dir = 'right'
        elif dx < 0:
            self.player.dir = 'left'
        elif dy > 0:
            self.player.dir = 'down'
        elif dy < 0:
            self.player.dir = 'up'

        nx = self.player.x + dx
        ny = self.player.y + dy

        # Check NPC collision
        if self.get_npc_at(nx, ny):
            return False

        # Check map collision
        if self.is_blocked(nx, ny):
            return False

        # Move
        self.player.x = nx
        self.player.y = ny

        # Check transitions
        trans = self.get_transition(nx, ny)
        if trans:
            self.load_map(trans['target'], trans['tx'], trans['ty'])
            self.add_message(f'Entered: {self.current_map["name"]}')
            return True

        # Check item pickups (walk-over)
        item = self.get_item_at(nx, ny)
        if item:
            if item.get('dialog'):
                self.show_dialog(item['dialog'])
            else:
                self.player.add_item(item['id'])
                self.add_message(f'Got: {ITEMS[item["id"]]["name"]}!')
            self.map_items.remove(item)

        return True

    def interact(self):
        """Interact with NPC or item in the direction the player faces."""
        tx, ty = self.player.x, self.player.y
        if self.player.dir == 'up':
            ty -= 1
        elif self.player.dir == 'down':
            ty += 1
        elif self.player.dir == 'left':
            tx -= 1
        elif self.player.dir == 'right':
            tx += 1

        # Check for NPC
        npc = self.get_npc_at(tx, ty)
        if npc:
            dialog_id = self.get_dialog_for_npc(npc['id'])
            if dialog_id:
                self.show_dialog(dialog_id)
            return True

        # Check for item
        item = self.get_item_at(tx, ty)
        if item:
            if item.get('dialog'):
                self.show_dialog(item['dialog'])
            else:
                self.player.add_item(item['id'])
                self.add_message(f'Got: {ITEMS[item["id"]]["name"]}!')
            self.map_items.remove(item)
            return True

        return False

    def update_enemies(self):
        """Move enemies along their patrol paths (turn-based: one step per player move)."""
        for e in self.enemies:
            if e['axis'] == 'x':
                e['x'] += e['dir']
                if e['x'] >= e['max']:
                    e['x'] = e['max']
                    e['dir'] = -1
                elif e['x'] <= e['min']:
                    e['x'] = e['min']
                    e['dir'] = 1
            else:
                e['y'] += e['dir']
                if e['y'] >= e['max']:
                    e['y'] = e['max']
                    e['dir'] = -1
                elif e['y'] <= e['min']:
                    e['y'] = e['min']
                    e['dir'] = 1

    def check_enemy_collision(self):
        """Check if player is on same tile as any enemy."""
        for e in self.enemies:
            if e['x'] == self.player.x and e['y'] == self.player.y:
                # Teleport player to map start
                sx, sy = self.current_map['player_start']
                self.player.x = sx
                self.player.y = sy
                self.add_message('A BUG got you! Back to the entrance...')
                return True
        return False

    def start_game(self):
        """Initialize/reset a new game."""
        self.player.reset()
        self.messages = []
        self.load_map('campus')
        self.state = 'playing'
        self.add_message('Welcome to HypeScale AI! Talk to people with SPACE.')

    # =========================================================================
    # Rendering
    # =========================================================================

    def render(self):
        """Main render dispatch."""
        self.stdscr.erase()
        h, w = self.stdscr.getmaxyx()

        if h < MIN_HEIGHT or w < MIN_WIDTH:
            self.render_size_warning(h, w)
            self.stdscr.refresh()
            return

        if self.state == 'title':
            self.render_title(h, w)
        elif self.state in ('playing', 'dialog', 'inventory'):
            self.render_game(h, w)
        elif self.state == 'ending':
            self.render_ending(h, w)

        self.stdscr.refresh()

    def render_size_warning(self, h, w):
        """Show terminal too small warning."""
        msg = f'Terminal too small: {w}x{h} (need {MIN_WIDTH}x{MIN_HEIGHT})'
        try:
            self.stdscr.addstr(0, 0, msg[:w])
        except curses.error:
            pass

    def render_title(self, h, w):
        """Render title screen."""
        safe_addstr(self.stdscr, 2, 2, '=' * 76, curses.color_pair(C_YELLOW) | curses.A_BOLD)

        # ASCII art title
        title_lines = [
            ' __  __ __     ______   ___                  _   ',
            '|  \\/  |\\ \\   / /  _ \\ / _ \\ _   _  ___ ___| |_ ',
            "| |\\/| | \\ \\ / /| |_) | | | | | | |/ _ / __| __|",
            '| |  | |  \\ V / |  __/| |_| | |_| |  __\\__ | |_ ',
            '|_|  |_|   \\_/  |_|    \\__\\_\\\\__,_|\\___|___/\\__|',
        ]
        for i, line in enumerate(title_lines):
            safe_addstr(self.stdscr, 4 + i, 15, line, curses.color_pair(C_YELLOW) | curses.A_BOLD)

        safe_addstr(self.stdscr, 10, 17, 'Ship the MVP. Save the Company.', curses.color_pair(C_RED) | curses.A_BOLD)
        safe_addstr(self.stdscr, 11, 27, '(Destroy Production.)', curses.color_pair(C_RED))

        safe_addstr(self.stdscr, 13, 8, '"Where every sprint is a marathon and every bug is a feature"',
                    curses.color_pair(C_GRAY))

        safe_addstr(self.stdscr, 15, 7, 'WASD / Arrows: Move  SPACE: Interact  I: Items  T: Tiles',
                    curses.color_pair(C_WHITE))

        # Blinking prompt
        now = time.time()
        if int(now * 2) % 2 == 0:
            safe_addstr(self.stdscr, 18, 24, 'PRESS SPACE TO START',
                        curses.color_pair(C_WHITE) | curses.A_BOLD)

        mode_label = 'Nerd Font' if not is_ascii_mode() else 'ASCII'
        safe_addstr(self.stdscr, 17, 25, f'Tile mode: {mode_label} (T to toggle)',
                    curses.color_pair(C_GRAY))

        safe_addstr(self.stdscr, 21, 20, 'A satirical RPG about AI hype culture',
                    curses.color_pair(C_GRAY))

        safe_addstr(self.stdscr, 22, 2, '=' * 76, curses.color_pair(C_YELLOW) | curses.A_BOLD)

    def render_game(self, h, w):
        """Render the game view: map + status + messages."""
        self.render_map_viewport()
        self.render_status_panel()
        self.render_message_bar()

        if self.state == 'dialog':
            self.render_dialog()
        elif self.state == 'inventory':
            self.render_inventory()

    def render_map_viewport(self):
        """Render the scrolling map viewport."""
        if not self.current_map:
            return

        grid = self.current_map['grid']
        map_h = len(grid)
        map_w = len(grid[0])

        # Camera: center on player, clamp to map bounds
        cam_x = self.player.x - MAP_VIEW_W // 2
        cam_y = self.player.y - MAP_VIEW_H // 2
        cam_x = max(0, min(cam_x, map_w - MAP_VIEW_W))
        cam_y = max(0, min(cam_y, map_h - MAP_VIEW_H))

        for vy in range(MAP_VIEW_H):
            for vx in range(MAP_VIEW_W):
                mx = cam_x + vx
                my = cam_y + vy

                if mx < 0 or my < 0 or mx >= map_w or my >= map_h:
                    safe_addstr(self.stdscr, vy, vx, ' ')
                    continue

                tile = grid[my][mx]
                glyph, color, attr = TILE_DISPLAY.get(tile, ('.', C_WHITE, 0))
                safe_addstr(self.stdscr, vy, vx, glyph,
                            curses.color_pair(color) | attr)

        # Draw items on ground
        for item in self.map_items:
            sx = item['x'] - cam_x
            sy = item['y'] - cam_y
            if 0 <= sx < MAP_VIEW_W and 0 <= sy < MAP_VIEW_H:
                safe_addstr(self.stdscr, sy, sx, GLYPH_ITEM_STAR,
                            curses.color_pair(C_ITEM) | curses.A_BOLD)

        # Draw enemies
        for e in self.enemies:
            sx = e['x'] - cam_x
            sy = e['y'] - cam_y
            if 0 <= sx < MAP_VIEW_W and 0 <= sy < MAP_VIEW_H:
                safe_addstr(self.stdscr, sy, sx, GLYPH_ENEMY,
                            curses.color_pair(C_ENEMY) | curses.A_BOLD)

        # Draw NPCs
        for npc in self.npcs:
            sx = npc['x'] - cam_x
            sy = npc['y'] - cam_y
            if 0 <= sx < MAP_VIEW_W and 0 <= sy < MAP_VIEW_H:
                safe_addstr(self.stdscr, sy, sx, npc['glyph'],
                            curses.color_pair(npc['color']) | curses.A_BOLD)

        # Draw player
        px = self.player.x - cam_x
        py = self.player.y - cam_y
        if 0 <= px < MAP_VIEW_W and 0 <= py < MAP_VIEW_H:
            safe_addstr(self.stdscr, py, px, GLYPH_PLAYER,
                        curses.color_pair(C_PLAYER) | curses.A_BOLD)

    def render_status_panel(self):
        """Render the right-side status panel."""
        sx = MAP_VIEW_W + 1  # starting x for status panel
        line = 0

        # Border line
        for y in range(MAP_VIEW_H):
            safe_addstr(self.stdscr, y, MAP_VIEW_W, '\u2502',
                        curses.color_pair(C_GRAY))  # │

        safe_addstr(self.stdscr, line, sx, 'MVPQuest',
                    curses.color_pair(C_YELLOW) | curses.A_BOLD)
        line += 1

        # Map name
        if self.current_map:
            name = self.current_map['name'][:STATUS_W - 1]
            safe_addstr(self.stdscr, line, sx, name,
                        curses.color_pair(C_WHITE))
        line += 2

        # Quest status
        p = self.player
        if p.quest_started:
            quest = QUEST_CHAIN[p.quest_step] if p.quest_step < len(QUEST_CHAIN) else None
            if quest:
                safe_addstr(self.stdscr, line, sx, 'Quest:',
                            curses.color_pair(C_YELLOW) | curses.A_BOLD)
                line += 1
                label = quest['label'][:STATUS_W - 1]
                safe_addstr(self.stdscr, line, sx, label,
                            curses.color_pair(C_WHITE))
                line += 1
                desc = quest['desc'][:STATUS_W - 1]
                safe_addstr(self.stdscr, line, sx, desc,
                            curses.color_pair(C_GRAY))
                line += 2

            # Artifact checklist
            safe_addstr(self.stdscr, line, sx, 'Artifacts:',
                        curses.color_pair(C_YELLOW) | curses.A_BOLD)
            line += 1
            artifacts = [
                ('has_yaml', 'YAML'),
                ('has_apikey', 'Key'),
                ('has_env', '.env'),
            ]
            for flag, label in artifacts:
                has = p.get_flag(flag)
                check = '\u2713' if has else '\u25cb'  # ✓ or ○
                color = C_GREEN if has else C_GRAY
                safe_addstr(self.stdscr, line, sx,
                            f' {check} {label}',
                            curses.color_pair(color))
                line += 1
            line += 1
        else:
            safe_addstr(self.stdscr, line, sx, 'Explore the campus',
                        curses.color_pair(C_GRAY))
            line += 1
            safe_addstr(self.stdscr, line, sx, 'and talk to people!',
                        curses.color_pair(C_GRAY))
            line += 2

        # Items count
        num_items = len(self.player.inventory)
        safe_addstr(self.stdscr, line, sx, f'Items: {num_items}',
                    curses.color_pair(C_WHITE))
        line += 2

        # Controls hint
        safe_addstr(self.stdscr, line, sx, '[I]nventory',
                    curses.color_pair(C_GRAY))
        line += 1
        safe_addstr(self.stdscr, line, sx, '[Q]uit',
                    curses.color_pair(C_GRAY))

    def render_message_bar(self):
        """Render the bottom message bar."""
        bar_y = MAP_VIEW_H

        # Separator line
        safe_addstr(self.stdscr, bar_y, 0, '\u2500' * MIN_WIDTH,
                    curses.color_pair(C_GRAY))  # ─

        # Messages
        for i, msg in enumerate(self.messages):
            safe_addstr(self.stdscr, bar_y + 1 + i, 1, msg[:MIN_WIDTH - 2],
                        curses.color_pair(C_WHITE))

        # Controls hint at bottom
        hints = '[SPACE] Talk  [I] Items  [T] Tiles  [Q] Quit'
        safe_addstr(self.stdscr, bar_y + MSG_H, 1, hints,
                    curses.color_pair(C_GRAY))

    def render_dialog(self):
        """Render dialog overlay box."""
        if not self.dialog_pages or self.dialog_page_idx >= len(self.dialog_pages):
            return

        page = self.dialog_pages[self.dialog_page_idx]
        speaker = page.get('speaker', '')
        text = page['text']

        # Update typewriter effect
        elapsed = time.time() - self.dialog_typewriter_time
        self.dialog_chars_shown = min(len(text), int(elapsed / 0.03))

        displayed_text = text[:self.dialog_chars_shown]

        # Dialog box dimensions
        box_w = MIN_WIDTH - 4
        box_h = 8
        box_x = 2
        box_y = MAP_VIEW_H - box_h - 1

        # Draw box background
        for dy in range(box_h):
            safe_addstr(self.stdscr, box_y + dy, box_x,
                        ' ' * box_w,
                        curses.color_pair(C_WHITE))

        # Border
        safe_addstr(self.stdscr, box_y, box_x,
                    '\u250c' + '\u2500' * (box_w - 2) + '\u2510',
                    curses.color_pair(C_YELLOW))  # ┌─┐
        safe_addstr(self.stdscr, box_y + box_h - 1, box_x,
                    '\u2514' + '\u2500' * (box_w - 2) + '\u2518',
                    curses.color_pair(C_YELLOW))  # └─┘
        for dy in range(1, box_h - 1):
            safe_addstr(self.stdscr, box_y + dy, box_x,
                        '\u2502', curses.color_pair(C_YELLOW))  # │
            safe_addstr(self.stdscr, box_y + dy, box_x + box_w - 1,
                        '\u2502', curses.color_pair(C_YELLOW))

        # Speaker name
        inner_x = box_x + 2
        inner_w = box_w - 4
        line_y = box_y + 1
        if speaker:
            safe_addstr(self.stdscr, line_y, inner_x, speaker,
                        curses.color_pair(C_YELLOW) | curses.A_BOLD)
            line_y += 1

        # Dialog text with word wrap
        lines = word_wrap(displayed_text, inner_w)
        for i, line in enumerate(lines):
            if line_y + i >= box_y + box_h - 2:
                break
            safe_addstr(self.stdscr, line_y + i, inner_x, line,
                        curses.color_pair(C_WHITE))

        # Prompt indicator
        if self.dialog_chars_shown >= len(text):
            prompt = '[ SPACE \u2192 ]' if self.dialog_page_idx < len(self.dialog_pages) - 1 else '[ SPACE \u2713 ]'
            safe_addstr(self.stdscr, box_y + box_h - 2, box_x + box_w - len(prompt) - 2,
                        prompt, curses.color_pair(C_GRAY))

    def render_inventory(self):
        """Render inventory overlay."""
        box_w = 50
        box_h = 14
        box_x = (MIN_WIDTH - box_w) // 2
        box_y = (MAP_VIEW_H - box_h) // 2

        # Clear area and draw border
        for dy in range(box_h):
            safe_addstr(self.stdscr, box_y + dy, box_x,
                        ' ' * box_w, curses.color_pair(C_WHITE))

        safe_addstr(self.stdscr, box_y, box_x,
                    '\u250c' + '\u2500' * (box_w - 2) + '\u2510',
                    curses.color_pair(C_YELLOW))
        safe_addstr(self.stdscr, box_y + box_h - 1, box_x,
                    '\u2514' + '\u2500' * (box_w - 2) + '\u2518',
                    curses.color_pair(C_YELLOW))
        for dy in range(1, box_h - 1):
            safe_addstr(self.stdscr, box_y + dy, box_x,
                        '\u2502', curses.color_pair(C_YELLOW))
            safe_addstr(self.stdscr, box_y + dy, box_x + box_w - 1,
                        '\u2502', curses.color_pair(C_YELLOW))

        # Title
        safe_addstr(self.stdscr, box_y + 1, box_x + 2,
                    'INVENTORY', curses.color_pair(C_YELLOW) | curses.A_BOLD)

        # Items
        if not self.player.inventory:
            safe_addstr(self.stdscr, box_y + 3, box_x + 2,
                        'Empty... go find some artifacts!',
                        curses.color_pair(C_GRAY))
        else:
            for i, item_id in enumerate(self.player.inventory):
                item = ITEMS.get(item_id)
                if not item:
                    continue
                row = box_y + 3 + i * 2
                if row >= box_y + box_h - 2:
                    break
                safe_addstr(self.stdscr, row, box_x + 2,
                            f'\u2605 {item["name"]}',
                            curses.color_pair(C_WHITE) | curses.A_BOLD)
                safe_addstr(self.stdscr, row + 1, box_x + 4,
                            item['desc'][:box_w - 6],
                            curses.color_pair(C_GRAY))

        # Close hint
        safe_addstr(self.stdscr, box_y + box_h - 2, box_x + 2,
                    'Press I or ESC to close',
                    curses.color_pair(C_GRAY))

    def render_ending(self, h, w):
        """Render scrolling ending text."""
        elapsed = time.time() - self.ending_timer
        scroll = int(elapsed * 1.5)  # ~1.5 lines per second
        self.ending_scroll = scroll

        for i, line in enumerate(ENDING_TEXT):
            y = h // 2 + i - scroll
            if y < 0 or y >= h:
                continue
            x = max(0, (w - len(line)) // 2)

            if 'M V P' in line or 'SHIPPED' in line:
                attr = curses.color_pair(C_YELLOW) | curses.A_BOLD
            elif 'PRESS' in line:
                blink = int(time.time() * 2) % 2
                attr = curses.color_pair(C_WHITE) | curses.A_BOLD if blink else curses.color_pair(C_GRAY)
            else:
                attr = curses.color_pair(C_WHITE)

            safe_addstr(self.stdscr, y, x, line, attr)

    # =========================================================================
    # Main loop
    # =========================================================================

    def run(self):
        """Main game loop."""
        # Curses setup
        curses.curs_set(0)
        self.stdscr.nodelay(False)
        self.stdscr.keypad(True)
        self.stdscr.timeout(100)  # 100ms timeout for getch (allows animation)

        init_colors()
        _build_tile_display()
        _load_settings()
        _apply_tileset()

        while True:
            self.render()

            try:
                key = self.stdscr.getch()
            except curses.error:
                continue

            if key == -1:
                continue  # Timeout, just re-render for animations

            if self.state == 'title':
                if key in (ord(' '), curses.KEY_ENTER, 10):
                    self.start_game()
                elif key in (ord('t'), ord('T')):
                    _toggle_tile_mode()
                elif key in (ord('q'), ord('Q')):
                    break

            elif self.state == 'playing':
                if key in (ord('q'), ord('Q')):
                    break
                elif key in (ord('t'), ord('T')):
                    _toggle_tile_mode()
                elif key in (curses.KEY_UP, ord('w'), ord('W')):
                    self.try_move(0, -1)
                    self.update_enemies()
                    self.check_enemy_collision()
                elif key in (curses.KEY_DOWN, ord('s'), ord('S')):
                    self.try_move(0, 1)
                    self.update_enemies()
                    self.check_enemy_collision()
                elif key in (curses.KEY_LEFT, ord('a'), ord('A')):
                    self.try_move(-1, 0)
                    self.update_enemies()
                    self.check_enemy_collision()
                elif key in (curses.KEY_RIGHT, ord('d'), ord('D')):
                    self.try_move(1, 0)
                    self.update_enemies()
                    self.check_enemy_collision()
                elif key in (ord(' '), curses.KEY_ENTER, 10):
                    self.interact()
                elif key in (ord('i'), ord('I')):
                    self.state = 'inventory'

            elif self.state == 'dialog':
                if key in (ord(' '), curses.KEY_ENTER, 10):
                    self.advance_dialog()

            elif self.state == 'inventory':
                if key in (ord('i'), ord('I'), 27):  # I or ESC
                    self.state = 'playing'

            elif self.state == 'ending':
                if key in (ord(' '), curses.KEY_ENTER, 10):
                    # Check if we're past the end
                    total = len(ENDING_TEXT) + MIN_HEIGHT
                    if self.ending_scroll > total - 5:
                        self.state = 'title'
                    else:
                        self.ending_timer -= 5  # Speed up scroll
                elif key in (ord('q'), ord('Q')):
                    break


# =============================================================================
# Helper functions
# =============================================================================

def init_colors():
    """Initialize curses color pairs."""
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(C_WHITE, curses.COLOR_WHITE, -1)
    curses.init_pair(C_GRAY, curses.COLOR_WHITE, -1)
    curses.init_pair(C_GREEN, curses.COLOR_GREEN, -1)
    curses.init_pair(C_YELLOW, curses.COLOR_YELLOW, -1)
    curses.init_pair(C_BLUE, curses.COLOR_BLUE, -1)
    curses.init_pair(C_RED, curses.COLOR_RED, -1)
    curses.init_pair(C_MAGENTA, curses.COLOR_MAGENTA, -1)
    curses.init_pair(C_CYAN, curses.COLOR_CYAN, -1)
    curses.init_pair(C_PLAYER, curses.COLOR_WHITE, -1)
    curses.init_pair(C_ENEMY, curses.COLOR_RED, -1)
    curses.init_pair(C_ITEM, curses.COLOR_YELLOW, -1)
    curses.init_pair(C_KAREN, curses.COLOR_RED, -1)
    curses.init_pair(C_MERLIN, curses.COLOR_MAGENTA, -1)
    curses.init_pair(C_DATADAVE, curses.COLOR_BLUE, -1)
    curses.init_pair(C_PRIYA, curses.COLOR_YELLOW, -1)
    curses.init_pair(C_ORACLE, curses.COLOR_CYAN, -1)
    curses.init_pair(C_STEVE, curses.COLOR_WHITE, -1)
    curses.init_pair(C_BOSS, curses.COLOR_RED, -1)
    curses.init_pair(C_DIM, curses.COLOR_WHITE, -1)
    curses.init_pair(C_BROWN, curses.COLOR_YELLOW, -1)


def safe_addstr(win, y, x, text, attr=0):
    """Write string to window, catching curses errors at edges."""
    h, w = win.getmaxyx()
    if y < 0 or y >= h or x < 0:
        return
    available = w - x
    if available <= 0:
        return
    text = str(text)[:available]
    try:
        win.addstr(y, x, text, attr)
    except curses.error:
        pass


def word_wrap(text, max_width):
    """Word-wrap text to max_width, respecting newlines."""
    lines = []
    for paragraph in text.split('\n'):
        if paragraph == '':
            lines.append('')
            continue
        words = paragraph.split(' ')
        line = ''
        for word in words:
            if line and len(line) + len(word) + 1 > max_width:
                lines.append(line)
                line = word
            else:
                line = f'{line} {word}'.strip() if line else word
        if line:
            lines.append(line)
    return lines


# =============================================================================
# Entry point
# =============================================================================

def main(stdscr):
    """Entry point wrapped by curses.wrapper."""
    game = Game(stdscr)
    game.run()


if __name__ == '__main__':
    curses.wrapper(main)
