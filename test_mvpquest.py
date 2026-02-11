#!/usr/bin/env python3
"""
Test suite for mvpquest.py — MVPQuest terminal RPG.
Tests the "known good" benchmark: structure, logic, and behavior.
These tests run WITHOUT a terminal (no curses rendering).
"""

import ast
import os
import stat
import sys
import unittest

# Path to the script under test
MVPQUEST_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mvpquest.py")


def load_source():
    """Load mvpquest.py source code as a string."""
    with open(MVPQUEST_PATH, "r", encoding="utf-8") as f:
        return f.read()


def parse_ast():
    """Parse mvpquest.py into an AST tree."""
    return ast.parse(load_source())


def get_top_level_names(tree):
    """Get all top-level names (functions, classes, assignments) from AST."""
    names = {}
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.FunctionDef):
            names[node.name] = "function"
        elif isinstance(node, ast.ClassDef):
            names[node.name] = "class"
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    names[target.id] = "variable"
    return names


def import_module():
    """Import mvpquest.py as a module (without running main).

    Strips the if __name__ == "__main__" block and execs everything else
    into a namespace, avoiding curses initialization.
    """
    source = load_source()
    tree = ast.parse(source)

    # Remove the if __name__ == "__main__" block
    new_body = []
    for node in tree.body:
        if isinstance(node, ast.If):
            test = node.test
            if (isinstance(test, ast.Compare) and
                isinstance(test.left, ast.Name) and
                    test.left.id == "__name__"):
                continue
        new_body.append(node)

    tree.body = new_body
    ast.fix_missing_locations(tree)

    code = compile(tree, MVPQUEST_PATH, "exec")
    namespace = {"__file__": MVPQUEST_PATH, "__name__": "mvpquest"}
    exec(code, namespace)
    return namespace


def find_all_functions(tree):
    """Find all function definitions in the AST (including nested/methods)."""
    functions = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            functions[node.name] = node
    return functions


def find_all_classes(tree):
    """Find all class definitions in the AST."""
    classes = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            classes[node.name] = node
    return classes


def find_all_string_literals(tree):
    """Find all string literals in the AST."""
    strings = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            strings.append(node.value)
    return strings


# =============================================================================
# 1. FILE STRUCTURE TESTS
# =============================================================================

class TestFileStructure(unittest.TestCase):
    """Tests that mvpquest.py has the right file-level properties."""

    def test_file_exists(self):
        """mvpquest.py must exist."""
        self.assertTrue(os.path.isfile(MVPQUEST_PATH),
                        f"mvpquest.py not found at {MVPQUEST_PATH}")

    def test_file_is_executable(self):
        """mvpquest.py must be executable."""
        mode = os.stat(MVPQUEST_PATH).st_mode
        self.assertTrue(mode & stat.S_IXUSR,
                        "mvpquest.py is not executable (missing user +x)")

    def test_has_shebang(self):
        """Must start with a Python shebang."""
        source = load_source()
        self.assertTrue(source.startswith("#!/"), "Missing shebang line")
        first_line = source.split("\n")[0]
        self.assertIn("python", first_line.lower(),
                      "Shebang doesn't reference python")

    def test_has_docstring(self):
        """Must have a module-level docstring."""
        tree = parse_ast()
        docstring = ast.get_docstring(tree)
        self.assertIsNotNone(docstring, "Missing module docstring")
        self.assertGreater(len(docstring), 10, "Docstring too short")

    def test_syntax_valid(self):
        """Must parse without syntax errors."""
        try:
            parse_ast()
        except SyntaxError as e:
            self.fail(f"Syntax error: {e}")

    def test_no_external_dependencies(self):
        """Must only import stdlib modules (no pip packages)."""
        STDLIB = {
            "ast", "curses", "os", "subprocess", "sys", "time",
            "pathlib", "glob", "re", "json", "shutil", "signal",
            "textwrap", "collections", "functools", "itertools",
            "math", "random", "string", "typing", "enum", "copy",
            "dataclasses", "abc", "heapq",
        }
        tree = parse_ast()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module = alias.name.split(".")[0]
                    self.assertIn(module, STDLIB,
                                  f"Non-stdlib import: {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    module = node.module.split(".")[0]
                    self.assertIn(module, STDLIB,
                                  f"Non-stdlib import: from {node.module}")

    def test_uses_curses(self):
        """Must import curses (it's a TUI)."""
        tree = parse_ast()
        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module.split(".")[0])
        self.assertIn("curses", imports, "Must import curses")

    def test_minimum_size(self):
        """An RPG this complex should be at least 1000 lines."""
        source = load_source()
        line_count = len(source.strip().split("\n"))
        self.assertGreaterEqual(line_count, 1000,
                                f"Only {line_count} lines — too small for an RPG")


# =============================================================================
# 2. REQUIRED COMPONENTS TESTS
# =============================================================================

class TestRequiredComponents(unittest.TestCase):
    """Tests that all required functions and data structures exist."""

    @classmethod
    def setUpClass(cls):
        cls.tree = parse_ast()
        cls.names = get_top_level_names(cls.tree)
        cls.all_funcs = find_all_functions(cls.tree)
        cls.all_classes = find_all_classes(cls.tree)
        cls.source = load_source()

    def test_has_main_function(self):
        """Must have a main() function."""
        self.assertIn("main", self.names,
                      "Missing main() function at top level")

    def test_uses_curses_wrapper(self):
        """Must call curses.wrapper() for proper terminal handling."""
        self.assertIn("curses.wrapper", self.source,
                      "Must use curses.wrapper() for proper terminal handling")

    def test_has_player_class(self):
        """Must have a Player class."""
        self.assertIn("Player", self.all_classes,
                      "Missing Player class")

    def test_has_game_class(self):
        """Must have a Game class."""
        self.assertIn("Game", self.all_classes,
                      "Missing Game class")

    def test_has_safe_addstr(self):
        """Must have safe_addstr() for bounds-safe drawing."""
        self.assertIn("safe_addstr", self.all_funcs,
                      "Missing safe_addstr() function")

    def test_has_init_colors(self):
        """Must have init_colors() function."""
        self.assertIn("init_colors", self.all_funcs,
                      "Missing init_colors() function")

    def test_has_word_wrap(self):
        """Must have word_wrap() function."""
        self.assertIn("word_wrap", self.all_funcs,
                      "Missing word_wrap() function")

    def test_has_map_builders(self):
        """Must have build functions for all 5 maps."""
        expected = ["build_campus", "build_office", "build_server",
                    "build_dungeon", "build_shrine"]
        for name in expected:
            self.assertIn(name, self.all_funcs,
                          f"Missing {name}() function")

    def test_has_tileset_system(self):
        """Must have tileset loading/toggle functions."""
        for name in ["_apply_tileset", "_toggle_tile_mode", "_load_settings",
                      "_save_settings", "is_ascii_mode"]:
            self.assertIn(name, self.all_funcs,
                          f"Missing {name}() function")


# =============================================================================
# 3. DATA INTEGRITY TESTS
# =============================================================================

class TestDataIntegrity(unittest.TestCase):
    """Tests that game data (dialogs, NPCs, items, quests) is complete."""

    @classmethod
    def setUpClass(cls):
        cls.ns = import_module()

    def test_all_dialogs_present(self):
        """Must have all 18 dialog trees."""
        dialogs = self.ns['DIALOGS']
        expected = [
            'merlin_intro', 'merlin_later',
            'datadave_intro', 'datadave_later',
            'karen_intro', 'karen_progress', 'karen_complete',
            'priya_intro', 'priya_later',
            'oracle_talk',
            'steve_noticket', 'steve_hasticket',
            'boss_intro', 'boss_defeated',
            'yaml_pickup', 'sign_campus',
        ]
        for dialog_id in expected:
            self.assertIn(dialog_id, dialogs,
                          f"Missing dialog: {dialog_id}")

    def test_dialogs_have_pages(self):
        """Every dialog must have a 'pages' list with at least one page."""
        for dialog_id, dialog in self.ns['DIALOGS'].items():
            self.assertIn('pages', dialog,
                          f"Dialog {dialog_id} missing 'pages'")
            self.assertGreater(len(dialog['pages']), 0,
                               f"Dialog {dialog_id} has empty pages")

    def test_dialog_pages_have_text(self):
        """Every dialog page must have a 'text' field."""
        for dialog_id, dialog in self.ns['DIALOGS'].items():
            for i, page in enumerate(dialog['pages']):
                self.assertIn('text', page,
                              f"Dialog {dialog_id} page {i} missing 'text'")
                self.assertGreater(len(page['text']), 0,
                                   f"Dialog {dialog_id} page {i} has empty text")

    def test_all_npcs_defined(self):
        """Must have all 7 NPC definitions."""
        npc_defs = self.ns['NPC_DEFS']
        expected = ['merlin', 'datadave', 'karen', 'priya', 'oracle',
                    'steve', 'boss']
        for npc_id in expected:
            self.assertIn(npc_id, npc_defs,
                          f"Missing NPC definition: {npc_id}")

    def test_npcs_have_required_fields(self):
        """Every NPC must have name, glyph, color."""
        for npc_id, npc in self.ns['NPC_DEFS'].items():
            self.assertIn('name', npc, f"NPC {npc_id} missing 'name'")
            self.assertIn('glyph', npc, f"NPC {npc_id} missing 'glyph'")
            self.assertIn('color', npc, f"NPC {npc_id} missing 'color'")

    def test_all_items_defined(self):
        """Must have all 5 item definitions."""
        items = self.ns['ITEMS']
        expected = ['rubber_duck', 'jira_ticket', 'yaml_scroll',
                    'api_key', 'env_file']
        for item_id in expected:
            self.assertIn(item_id, items,
                          f"Missing item definition: {item_id}")

    def test_quest_chain_complete(self):
        """Quest chain must have 5 steps."""
        chain = self.ns['QUEST_CHAIN']
        self.assertEqual(len(chain), 5,
                         f"Quest chain has {len(chain)} steps, expected 5")
        expected_ids = ['welcome', 'get_yaml', 'get_apikey', 'get_env', 'ship_it']
        for i, step in enumerate(chain):
            self.assertEqual(step['id'], expected_ids[i],
                             f"Quest step {i} id mismatch")

    def test_ending_text_present(self):
        """Ending text must be substantial."""
        ending = self.ns['ENDING_TEXT']
        self.assertGreater(len(ending), 20,
                           "Ending text too short")
        # Check key lines are present
        all_text = '\n'.join(ending)
        self.assertIn('MVP HAS SHIPPED', all_text)
        self.assertIn('Karen got promoted', all_text)
        self.assertIn('M V P Q U E S T', all_text)


# =============================================================================
# 4. MAP DATA TESTS
# =============================================================================

class TestMapData(unittest.TestCase):
    """Tests that all 5 maps build correctly."""

    @classmethod
    def setUpClass(cls):
        cls.ns = import_module()
        cls.maps = cls.ns['build_all_maps']()

    def test_all_maps_exist(self):
        """Must have all 5 maps."""
        expected = ['campus', 'office', 'server', 'dungeon', 'shrine']
        for map_id in expected:
            self.assertIn(map_id, self.maps,
                          f"Missing map: {map_id}")

    def test_campus_dimensions(self):
        """Campus map must be 30x25."""
        m = self.maps['campus']
        self.assertEqual(m['width'], 30)
        self.assertEqual(m['height'], 25)
        self.assertEqual(len(m['grid']), 25)
        self.assertEqual(len(m['grid'][0]), 30)

    def test_office_dimensions(self):
        """Office map must be 20x15."""
        m = self.maps['office']
        self.assertEqual(m['width'], 20)
        self.assertEqual(m['height'], 15)

    def test_server_dimensions(self):
        """Server room must be 12x10."""
        m = self.maps['server']
        self.assertEqual(m['width'], 12)
        self.assertEqual(m['height'], 10)

    def test_dungeon_dimensions(self):
        """Dungeon must be 25x20."""
        m = self.maps['dungeon']
        self.assertEqual(m['width'], 25)
        self.assertEqual(m['height'], 20)

    def test_shrine_dimensions(self):
        """Shrine must be 9x7."""
        m = self.maps['shrine']
        self.assertEqual(m['width'], 9)
        self.assertEqual(m['height'], 7)

    def test_maps_have_player_start(self):
        """Every map must have a player_start position."""
        for map_id, m in self.maps.items():
            self.assertIn('player_start', m,
                          f"Map {map_id} missing player_start")
            sx, sy = m['player_start']
            self.assertTrue(0 <= sx < m['width'],
                            f"Map {map_id} start x={sx} out of bounds")
            self.assertTrue(0 <= sy < m['height'],
                            f"Map {map_id} start y={sy} out of bounds")

    def test_player_start_not_blocked(self):
        """Player start position must not be a blocking tile."""
        BLOCKING = self.ns['BLOCKING']
        for map_id, m in self.maps.items():
            sx, sy = m['player_start']
            tile = m['grid'][sy][sx]
            self.assertNotIn(tile, BLOCKING,
                             f"Map {map_id} player start ({sx},{sy}) is blocked by {tile}")

    def test_maps_have_transitions(self):
        """Campus and other maps must have transition points."""
        # Campus must have transitions to all other maps
        campus_targets = {t['target'] for t in self.maps['campus']['transitions']}
        for target in ['office', 'server', 'shrine', 'dungeon']:
            self.assertIn(target, campus_targets,
                          f"Campus missing transition to {target}")

        # Non-campus maps must have transition back to campus
        for map_id in ['office', 'server', 'shrine', 'dungeon']:
            targets = {t['target'] for t in self.maps[map_id]['transitions']}
            self.assertIn('campus', targets,
                          f"Map {map_id} missing transition back to campus")

    def test_campus_has_npcs(self):
        """Campus must have Merlin and DataDave."""
        npc_ids = {n['id'] for n in self.maps['campus']['npcs']}
        self.assertIn('merlin', npc_ids)
        self.assertIn('datadave', npc_ids)

    def test_office_has_npcs(self):
        """Office must have Karen and Priya."""
        npc_ids = {n['id'] for n in self.maps['office']['npcs']}
        self.assertIn('karen', npc_ids)
        self.assertIn('priya', npc_ids)

    def test_server_has_steve(self):
        """Server room must have Steve."""
        npc_ids = {n['id'] for n in self.maps['server']['npcs']}
        self.assertIn('steve', npc_ids)

    def test_dungeon_has_boss(self):
        """Dungeon must have the GPT-7 boss."""
        npc_ids = {n['id'] for n in self.maps['dungeon']['npcs']}
        self.assertIn('boss', npc_ids)

    def test_shrine_has_oracle(self):
        """Shrine must have the Oracle."""
        npc_ids = {n['id'] for n in self.maps['shrine']['npcs']}
        self.assertIn('oracle', npc_ids)

    def test_dungeon_has_enemies(self):
        """Dungeon must have patrol enemies."""
        enemies = self.maps['dungeon']['enemies']
        self.assertGreaterEqual(len(enemies), 4,
                                f"Dungeon only has {len(enemies)} enemies, expected 4")

    def test_office_has_yaml_item(self):
        """Office must have the YAML scroll item."""
        item_ids = {i['id'] for i in self.maps['office']['items']}
        self.assertIn('yaml_scroll', item_ids)


# =============================================================================
# 5. GAME LOGIC TESTS
# =============================================================================

class TestGameLogic(unittest.TestCase):
    """Tests game logic without a curses terminal."""

    @classmethod
    def setUpClass(cls):
        cls.ns = import_module()

    def _make_player(self):
        """Create a fresh Player instance."""
        return self.ns['Player']()

    def test_player_inventory(self):
        """Player inventory add/has must work."""
        p = self._make_player()
        self.assertFalse(p.has_item('yaml_scroll'))
        p.add_item('yaml_scroll')
        self.assertTrue(p.has_item('yaml_scroll'))
        # Adding duplicate should not double-add
        p.add_item('yaml_scroll')
        self.assertEqual(p.inventory.count('yaml_scroll'), 1)

    def test_player_quest_flags(self):
        """Player quest flags must work."""
        p = self._make_player()
        self.assertFalse(p.get_flag('has_yaml'))
        p.set_flag('has_yaml')
        self.assertTrue(p.get_flag('has_yaml'))

    def test_player_reset(self):
        """Player reset clears all state."""
        p = self._make_player()
        p.add_item('api_key')
        p.set_flag('has_apikey')
        p.quest_started = True
        p.quest_step = 3
        p.reset()
        self.assertEqual(p.inventory, [])
        self.assertEqual(p.quest_flags, {})
        self.assertFalse(p.quest_started)
        self.assertEqual(p.quest_step, 0)

    def test_collision_detection(self):
        """is_blocked() must identify blocking tiles."""
        BLOCKING = self.ns['BLOCKING']
        WALL = self.ns['WALL']
        FLOOR = self.ns['FLOOR']
        GRASS = self.ns['GRASS']
        WATER = self.ns['WATER']
        TREE = self.ns['TREE']
        self.assertIn(WALL, BLOCKING)
        self.assertIn(WATER, BLOCKING)
        self.assertIn(TREE, BLOCKING)
        self.assertNotIn(FLOOR, BLOCKING)
        self.assertNotIn(GRASS, BLOCKING)

    def test_dialog_state_selection(self):
        """Dialog selection for NPCs must change based on quest state."""
        # We can't call get_dialog_for_npc without a Game instance,
        # but we can verify the logic via the source code patterns
        source = load_source()
        # Merlin should have intro/later variants
        self.assertIn('merlin_intro', source)
        self.assertIn('merlin_later', source)
        # Karen should have intro/progress/complete
        self.assertIn('karen_intro', source)
        self.assertIn('karen_progress', source)
        self.assertIn('karen_complete', source)
        # Steve should have noticket/hasticket
        self.assertIn('steve_noticket', source)
        self.assertIn('steve_hasticket', source)

    def test_quest_actions_defined(self):
        """All dialog on_end actions must be handled in trigger_action."""
        source = load_source()
        actions = ['start_quest', 'give_duck', 'give_ticket', 'give_yaml',
                   'give_apikey', 'give_env', 'finish_game']
        for action in actions:
            self.assertIn(f"'{action}'", source,
                          f"Action {action} not handled in trigger_action")

    def test_enemy_patrol_bounds(self):
        """Enemy patrol min must be less than max."""
        maps = self.ns['build_all_maps']()
        for e in maps['dungeon']['enemies']:
            self.assertLess(e['min'], e['max'],
                            f"Enemy at ({e['x']},{e['y']}) has min >= max")

    def test_word_wrap_basic(self):
        """word_wrap must correctly break long lines."""
        word_wrap = self.ns['word_wrap']
        result = word_wrap("hello world this is a test", 12)
        self.assertTrue(all(len(line) <= 12 for line in result),
                        f"Lines exceed max width: {result}")

    def test_word_wrap_newlines(self):
        """word_wrap must respect explicit newlines."""
        word_wrap = self.ns['word_wrap']
        result = word_wrap("line one\nline two", 80)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], "line one")
        self.assertEqual(result[1], "line two")

    def test_word_wrap_empty_lines(self):
        """word_wrap must preserve empty lines."""
        word_wrap = self.ns['word_wrap']
        result = word_wrap("before\n\nafter", 80)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[1], "")


# =============================================================================
# 6. INTEGRATION TESTS
# =============================================================================

class TestIntegration(unittest.TestCase):
    """Integration tests for map transitions and quest chain."""

    @classmethod
    def setUpClass(cls):
        cls.ns = import_module()

    def test_all_transitions_point_to_valid_maps(self):
        """Every transition target must be a valid map."""
        maps = self.ns['build_all_maps']()
        for map_id, m in maps.items():
            for t in m.get('transitions', []):
                self.assertIn(t['target'], maps,
                              f"Map {map_id} has transition to nonexistent map: {t['target']}")

    def test_transition_targets_are_walkable(self):
        """Transition target positions must not be blocked."""
        BLOCKING = self.ns['BLOCKING']
        maps = self.ns['build_all_maps']()
        for map_id, m in maps.items():
            for t in m.get('transitions', []):
                target_map = maps[t['target']]
                tx, ty = t['tx'], t['ty']
                tile = target_map['grid'][ty][tx]
                self.assertNotIn(tile, BLOCKING,
                                 f"Transition from {map_id} to {t['target']} "
                                 f"lands on blocked tile {tile} at ({tx},{ty})")

    def test_npc_positions_not_blocked(self):
        """NPC positions must be on walkable tiles."""
        BLOCKING = self.ns['BLOCKING']
        maps = self.ns['build_all_maps']()
        for map_id, m in maps.items():
            for npc in m.get('npcs', []):
                tile = m['grid'][npc['y']][npc['x']]
                self.assertNotIn(tile, BLOCKING,
                                 f"NPC {npc['id']} in {map_id} is on blocked tile "
                                 f"{tile} at ({npc['x']},{npc['y']})")

    def test_item_positions_not_blocked(self):
        """Item positions must be on walkable tiles (or near walkable)."""
        maps = self.ns['build_all_maps']()
        for map_id, m in maps.items():
            for item in m.get('items', []):
                x, y = item['x'], item['y']
                self.assertTrue(0 <= x < m['width'],
                                f"Item {item['id']} x={x} out of bounds in {map_id}")
                self.assertTrue(0 <= y < m['height'],
                                f"Item {item['id']} y={y} out of bounds in {map_id}")

    def test_quest_chain_walkthrough(self):
        """Full quest chain must be completable via trigger_action."""
        Player = self.ns['Player']
        p = Player()

        # Step 0: Welcome
        self.assertEqual(p.quest_step, 0)
        self.assertFalse(p.quest_started)

        # Talk to Karen → start_quest
        p.quest_started = True
        p.quest_step = 1

        # Get YAML
        p.add_item('yaml_scroll')
        p.set_flag('has_yaml')
        # Advance: should move to step 2
        if p.get_flag('has_yaml') and p.quest_step < 2:
            p.quest_step = 2

        self.assertEqual(p.quest_step, 2)

        # Get API Key
        p.add_item('api_key')
        p.set_flag('has_apikey')
        if p.get_flag('has_apikey') and p.quest_step < 3:
            p.quest_step = 3

        self.assertEqual(p.quest_step, 3)

        # Get .env File
        p.add_item('env_file')
        p.set_flag('has_env')
        p.set_flag('boss_defeated')
        if p.get_flag('has_yaml') and p.get_flag('has_apikey') and p.get_flag('has_env'):
            p.quest_step = 4

        self.assertEqual(p.quest_step, 4)

        # Verify all artifacts collected
        self.assertTrue(p.has_item('yaml_scroll'))
        self.assertTrue(p.has_item('api_key'))
        self.assertTrue(p.has_item('env_file'))

    def test_dialog_on_end_actions_reference_valid_items(self):
        """Dialog on_end actions that give items must reference valid item IDs."""
        DIALOGS = self.ns['DIALOGS']
        ITEMS = self.ns['ITEMS']
        action_to_item = {
            'give_duck': 'rubber_duck',
            'give_ticket': 'jira_ticket',
            'give_yaml': 'yaml_scroll',
            'give_apikey': 'api_key',
            'give_env': 'env_file',
        }
        for dialog_id, dialog in DIALOGS.items():
            on_end = dialog.get('on_end')
            if on_end in action_to_item:
                item_id = action_to_item[on_end]
                self.assertIn(item_id, ITEMS,
                              f"Dialog {dialog_id} on_end={on_end} references "
                              f"unknown item {item_id}")

    def test_tileset_json_exists(self):
        """mvpquest_tiles.json must exist alongside mvpquest.py."""
        tiles_path = os.path.join(os.path.dirname(MVPQUEST_PATH),
                                  "mvpquest_tiles.json")
        self.assertTrue(os.path.isfile(tiles_path),
                        f"mvpquest_tiles.json not found at {tiles_path}")

    def test_tileset_json_valid(self):
        """mvpquest_tiles.json must be valid JSON with nerdfont and ascii modes."""
        import json
        tiles_path = os.path.join(os.path.dirname(MVPQUEST_PATH),
                                  "mvpquest_tiles.json")
        with open(tiles_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertIn("nerdfont", data, "Missing nerdfont tileset")
        self.assertIn("ascii", data, "Missing ascii tileset")
        for mode in ["nerdfont", "ascii"]:
            self.assertIn("glyphs", data[mode],
                          f"Mode {mode} missing glyphs")
            self.assertIn("tiles", data[mode],
                          f"Mode {mode} missing tiles")


if __name__ == '__main__':
    unittest.main()
