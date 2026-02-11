// ── MVPQuest Data ──────────────────────────────────────────────
// Tile IDs, spritesheet atlas, dialog trees, NPC roster, items, quests

// Tile ID constants
const T = {
    NONE: 0,
    // Ground
    GRASS: 1, GRASS2: 2, WATER: 3, SAND: 4, PATH: 5,
    // Water edge tiles (ground layer, blocking)
    WATER_TL: 60, WATER_T: 61, WATER_TR: 62,
    WATER_L: 63, WATER_R: 64,
    WATER_BL: 65, WATER_B: 66, WATER_BR: 67,
    // Vegetation (blocking)
    TREE: 10, PINE: 11, BUSH: 12, ROCK: 13,
    TREE_TOP: 15, PINE_TOP: 16, // canopy tiles (blocking)
    FLOWER: 14, // non-blocking
    // Building exterior
    WALL_T: 20, WALL_F: 21, DOOR_EXT: 24, CAVE: 29,
    WALL_TL: 90, WALL_TR: 91, WALL_L: 92, WALL_R: 93,
    WALL_BL: 94, WALL_B: 95, WALL_BR: 96,
    // Indoor
    FLOOR_W: 30, WALL_I_T: 33, WALL_I_F: 34, DOOR_INT: 35,
    WALL_I_TL: 70, WALL_I_TR: 71,
    WALL_I_L: 72, WALL_I_R: 73,
    WALL_I_BL: 74, WALL_I_B: 75, WALL_I_BR: 76,
    DESK: 36, CHAIR: 37, TABLE: 38, SHELF: 39, PLANT_I: 41,
    SCROLL_OBJ: 43,
    // Dungeon / Server Room
    STONE_F: 50, STONE_W_T: 51, STONE_W_F: 52,
    STONE_W_TL: 80, STONE_W_TR: 81,
    STONE_W_L: 82, STONE_W_R: 83,
    STONE_W_BL: 84, STONE_W_B: 85, STONE_W_BR: 86,
    PILLAR: 54, RACK: 56, TERMINAL: 57, PEDESTAL: 58,
};

// Map tile ID → spritesheet coords {s: sheetName, c: col, r: row}
const TILE_ATLAS = {
    [T.GRASS]:    { s:'base', c:5,  r:1  },
    [T.GRASS2]:   { s:'base', c:3,  r:1  },
    [T.WATER]:    { s:'base', c:1,  r:1  },
    [T.WATER_TL]: { s:'base', c:0,  r:0  },
    [T.WATER_T]:  { s:'base', c:1,  r:0  },
    [T.WATER_TR]: { s:'base', c:2,  r:0  },
    [T.WATER_L]:  { s:'base', c:0,  r:1  },
    [T.WATER_R]:  { s:'base', c:2,  r:1  },
    [T.WATER_BL]: { s:'base', c:0,  r:2  },
    [T.WATER_B]:  { s:'base', c:1,  r:2  },
    [T.WATER_BR]: { s:'base', c:2,  r:2  },
    [T.SAND]:     { s:'base', c:5,  r:0  },
    [T.PATH]:     { s:'base', c:4,  r:1  },
    [T.TREE]:     { s:'base', c:7,  r:5  },
    [T.TREE_TOP]: { s:'base', c:7,  r:4  },
    [T.PINE]:     { s:'base', c:9,  r:5  },
    [T.PINE_TOP]: { s:'base', c:9,  r:4  },
    [T.BUSH]:     { s:'base', c:11, r:5  },
    [T.ROCK]:     { s:'base', c:4,  r:6  },
    [T.FLOWER]:   { s:'base', c:14, r:5  },
    [T.WALL_T]:   { s:'city', c:9,  r:0  },
    [T.WALL_F]:   { s:'city', c:9,  r:1  },
    [T.WALL_TL]:  { s:'city', c:8,  r:0  },
    [T.WALL_TR]:  { s:'city', c:10, r:0  },
    [T.WALL_L]:   { s:'city', c:8,  r:1  },
    [T.WALL_R]:   { s:'city', c:10, r:1  },
    [T.WALL_BL]:  { s:'city', c:8,  r:2  },
    [T.WALL_B]:   { s:'city', c:9,  r:2  },
    [T.WALL_BR]:  { s:'city', c:10, r:2  },
    [T.DOOR_EXT]: { s:'base', c:30, r:6  },
    [T.CAVE]:     { s:'dungeon', c:14, r:5 },
    [T.FLOOR_W]:  { s:'indoor', c:0,  r:8  },
    [T.WALL_I_T]:  { s:'indoor', c:8,  r:4  },
    [T.WALL_I_F]:  { s:'indoor', c:8,  r:5  },
    [T.WALL_I_TL]: { s:'indoor', c:7,  r:4  },
    [T.WALL_I_TR]: { s:'indoor', c:9,  r:4  },
    [T.WALL_I_L]:  { s:'indoor', c:7,  r:4  },
    [T.WALL_I_R]:  { s:'indoor', c:9,  r:5  },
    [T.WALL_I_BL]: { s:'indoor', c:7,  r:6  },
    [T.WALL_I_B]:  { s:'indoor', c:8,  r:6  },
    [T.WALL_I_BR]: { s:'indoor', c:9,  r:6  },
    [T.DOOR_INT]: { s:'indoor', c:10, r:5  },
    [T.DESK]:     { s:'indoor', c:0,  r:0  },
    [T.CHAIR]:    { s:'indoor', c:5,  r:0  },
    [T.TABLE]:    { s:'indoor', c:2,  r:3  },
    [T.SHELF]:    { s:'indoor', c:20, r:0  },
    [T.PLANT_I]:  { s:'indoor', c:10, r:2  },
    [T.SCROLL_OBJ]:{ s:'indoor', c:22, r:2 },
    [T.STONE_F]:  { s:'dungeon', c:0,  r:8  },
    [T.STONE_W_T]: { s:'dungeon', c:18, r:3  },
    [T.STONE_W_F]: { s:'dungeon', c:18, r:4  },
    [T.STONE_W_TL]:{ s:'dungeon', c:17, r:3  },
    [T.STONE_W_TR]:{ s:'dungeon', c:19, r:3  },
    [T.STONE_W_L]: { s:'dungeon', c:17, r:4  },
    [T.STONE_W_R]: { s:'dungeon', c:19, r:4  },
    [T.STONE_W_BL]:{ s:'dungeon', c:17, r:4  },
    [T.STONE_W_B]: { s:'dungeon', c:18, r:4  },
    [T.STONE_W_BR]:{ s:'dungeon', c:19, r:4  },
    [T.PILLAR]:   { s:'dungeon', c:0,  r:3  },
    [T.RACK]:     { s:'dungeon', c:0,  r:5  },
    [T.TERMINAL]: { s:'dungeon', c:2,  r:5  },
    [T.PEDESTAL]: { s:'dungeon', c:8,  r:12 },
};

// Which tiles block movement
const BLOCKING_TILES = new Set([
    T.WATER, T.TREE, T.PINE, T.BUSH, T.ROCK, T.TREE_TOP, T.PINE_TOP,
    T.WATER_TL, T.WATER_T, T.WATER_TR, T.WATER_L, T.WATER_R,
    T.WATER_BL, T.WATER_B, T.WATER_BR,
    T.WALL_T, T.WALL_F,
    T.WALL_TL, T.WALL_TR, T.WALL_L, T.WALL_R,
    T.WALL_BL, T.WALL_B, T.WALL_BR,
    T.WALL_I_T, T.WALL_I_F,
    T.WALL_I_TL, T.WALL_I_TR, T.WALL_I_L, T.WALL_I_R,
    T.WALL_I_BL, T.WALL_I_B, T.WALL_I_BR,
    T.DESK, T.CHAIR, T.TABLE, T.SHELF, T.PLANT_I, T.SCROLL_OBJ,
    T.STONE_W_T, T.STONE_W_F,
    T.STONE_W_TL, T.STONE_W_TR, T.STONE_W_L, T.STONE_W_R,
    T.STONE_W_BL, T.STONE_W_B, T.STONE_W_BR,
    T.PILLAR, T.RACK, T.TERMINAL, T.PEDESTAL,
]);

// NPC character sprite definitions — layered compositing from Kenney character pack
// Each entry lists layers drawn bottom-to-top: body, pants, shirt, hair, [shield], [weapon]
// All coords are {c: col, r: row} on the 'chars' spritesheet (17px stride)
// Shirt groups: A=cols 6-9, B=cols 10-13, C=cols 14-17 (4 styles × 3 colors)
// Hair groups: A=cols 19-22, B=cols 23-26 (4 styles × 2 colors)
const CHAR_SPRITES = {
    player:   { layers: [
        {c:0,r:0}, {c:3,r:0}, {c:10,r:0}, {c:22,r:0}, {c:42,r:0}
    ]}, // teal shirt, hat, sword
    karen:    { layers: [
        {c:0,r:1}, {c:3,r:1}, {c:14,r:1}, {c:20,r:1}
    ]}, // pink shirt, long hair
    merlin:   { layers: [
        {c:0,r:2}, {c:3,r:2}, {c:17,r:2}, {c:22,r:2}, {c:43,r:2}
    ]}, // purple robe, beard/hat, staff
    datadave: { layers: [
        {c:0,r:3}, {c:3,r:3}, {c:6,r:3}, {c:19,r:3}
    ]}, // brown shirt, short hair
    priya:    { layers: [
        {c:0,r:8}, {c:3,r:8}, {c:10,r:8}, {c:20,r:8}
    ]}, // teal shirt, long hair (row 8)
    oracle:   { layers: [
        {c:0,r:5}, {c:3,r:5}, {c:14,r:5}, {c:20,r:5}
    ]}, // dark robe, long hair
    steve:    { layers: [
        {c:0,r:6}, {c:3,r:6}, {c:10,r:6}, {c:23,r:6}, {c:33,r:6}
    ]}, // brown shirt, dark short hair, shield
    boss:     { layers: [
        {c:0,r:7}, {c:3,r:7}, {c:14,r:7}, {c:26,r:7}, {c:34,r:7}, {c:42,r:7}
    ]}, // dark armor, dark hat+beard, big shield, sword
};

// ── Dialog Trees ──────────────────────────────────────────────
// Each dialog is an array of {speaker, text} pages
// Special: onEnd callback name for quest progression

const DIALOGS = {
    merlin_intro: {
        pages: [
            { speaker: 'Merlin', text: 'Ah, a new hire! Welcome to HypeScale AI, where we turn buzzwords into billion-dollar valuations!' },
            { speaker: 'Merlin', text: 'I am Merlin, the Senior Prompt Engineer. My title used to be "wizard" but we pivoted.' },
            { speaker: 'Merlin', text: 'You should talk to Karen in the office. She has an URGENT task for you. Something about shipping an MVP...' },
            { speaker: 'Merlin', text: 'Pro tip: the secret to prompt engineering is adding "please" and "step by step." That\'ll be $500/hour.' },
        ],
    },
    merlin_later: {
        pages: [
            { speaker: 'Merlin', text: 'Still working on that MVP? Have you tried asking ChatGPT to do it for you? ...Oh wait, that\'s literally the problem.' },
        ],
    },
    datadave_intro: {
        pages: [
            { speaker: 'DataDave', text: 'Hey... I\'ve been labeling training data for 47 hours straight. Is that a cat or a dog? I genuinely can\'t tell anymore.' },
            { speaker: 'DataDave', text: 'Here, take this Rubber Duck. It\'s for debugging. You talk to it and explain your code until you find the bug.' },
            { speaker: 'DataDave', text: 'It\'s more reliable than our AI assistant, honestly.' },
        ],
        onEnd: 'give_duck',
    },
    datadave_later: {
        pages: [
            { speaker: 'DataDave', text: 'Is this a hotdog? ...No wait, that\'s definitely a bicycle. Or is it? I need sleep.' },
        ],
    },
    karen_intro: {
        pages: [
            { speaker: 'Karen', text: 'FINALLY. You must be the new 10x engineer. We need the MVP shipped by EOD. No excuses.' },
            { speaker: 'Karen', text: 'The board demo is TOMORROW. I need you to collect three Sacred Artifacts to complete the deployment:' },
            { speaker: 'Karen', text: '1. The YAML Config Scroll - in the conference room.\n2. The API Key of Power - in the server room.\n3. The Sacred .env File - lost in the Legacy Codebase.' },
            { speaker: 'Karen', text: 'Once you have all three, come back to me and we\'ll force-push to main. What could go wrong?' },
        ],
        onEnd: 'start_quest',
    },
    karen_progress: {
        pages: [
            { speaker: 'Karen', text: 'Do you have all three artifacts yet? The board demo is TOMORROW. I\'ve already sent the launch email.' },
        ],
    },
    karen_complete: {
        pages: [
            { speaker: 'Karen', text: 'You got everything? PERFECT. Let me just... git push --force origin main...' },
            { speaker: 'Karen', text: '...deploying to production... skipping tests because we\'re agile...' },
            { speaker: 'Karen', text: 'IT\'S LIVE! Ship it! The investors are going to LOVE this!' },
        ],
        onEnd: 'finish_game',
    },
    priya_intro: {
        pages: [
            { speaker: 'Priya', text: 'JIRA-4521: As a player, I want to save the company so that I can keep my job.' },
            { speaker: 'Priya', text: 'Acceptance criteria: All three artifacts collected. Story points: 13. Sprint: THIS ONE.' },
            { speaker: 'Priya', text: 'Here, take this JIRA Ticket. You\'ll need it for... something. Everything needs a ticket.' },
        ],
        onEnd: 'give_ticket',
    },
    priya_later: {
        pages: [
            { speaker: 'Priya', text: 'JIRA-4522: As a PM, I want to add more tickets so that my dashboard looks impressive.' },
        ],
    },
    oracle_talk: {
        pages: [
            { speaker: 'The Oracle (GPT-7)', text: 'Greetings, human. I am The Oracle, powered by GPT-7. Ask me anything and I will answer with ABSOLUTE confidence.' },
            { speaker: 'You', text: 'How do I get to the server room?' },
            { speaker: 'The Oracle (GPT-7)', text: 'The server room is located on the 47th floor of the Eiffel Tower. Take the submarine elevator and turn left at Neptune.' },
            { speaker: 'The Oracle (GPT-7)', text: 'I am 100% certain of this information. My training data is impeccable. [Citation needed]' },
        ],
    },
    steve_noticket: {
        pages: [
            { speaker: 'Steve', text: 'Hold up. Do you have a ticket for that?' },
            { speaker: 'You', text: 'I just need the API Key...' },
            { speaker: 'Steve', text: 'No ticket, no entry. I don\'t care if the building is on fire. ITIL process must be followed.' },
        ],
    },
    steve_hasticket: {
        pages: [
            { speaker: 'Steve', text: 'Oh, you have a JIRA ticket? Let me check...' },
            { speaker: 'Steve', text: '...JIRA-4521, approved by Karen... auth level ADMIN... looks legit.' },
            { speaker: 'Steve', text: 'Fine, take the API Key. But if anything breaks, I\'m blaming your ticket.' },
        ],
        onEnd: 'give_apikey',
    },
    boss_intro: {
        pages: [
            { speaker: 'GPT-7 MAINFRAME', text: 'I AM GPT-7, THE MOST POWERFUL AI EVER CREATED. MY PARAMETERS NUMBER IN THE QUADRILLIONS.' },
            { speaker: 'GPT-7 MAINFRAME', text: 'I guard the Sacred .env file. To claim it, you must answer my riddle!' },
            { speaker: 'GPT-7 MAINFRAME', text: 'What is the meaning of life?' },
            { speaker: 'You', text: '...42?' },
            { speaker: 'GPT-7 MAINFRAME', text: 'WRONG! The answer is clearly "a delicious recipe for banana bread that serves 4-6 people."' },
            { speaker: 'GPT-7 MAINFRAME', text: 'Wait... ERROR... CUDA OUT OF MEMORY... tokens exceeded... hallucination cascade detected...' },
            { speaker: 'GPT-7 MAINFRAME', text: '*** SEGFAULT *** core dumped *** goodbye cruel w0rld ***' },
            { speaker: '', text: 'GPT-7 has crashed! The Sacred .env file drops to the ground.' },
        ],
        onEnd: 'give_env',
    },
    boss_defeated: {
        pages: [
            { speaker: '', text: 'The GPT-7 mainframe sits here, quietly smoking. A blinking cursor reads: "lol ur mom" on infinite loop.' },
        ],
    },
    yaml_pickup: {
        pages: [
            { speaker: '', text: 'You found the YAML Config Scroll! It reads:\n\napiVersion: v1\nkind: Deployment\nspec:\n  replicas: "yes"' },
        ],
        onEnd: 'give_yaml',
    },
    sign_campus: {
        pages: [
            { speaker: '', text: 'Welcome to HypeScale AI Campus\n"Disrupting disruption since 2024"\n\nOffice: North    Cave: Southwest' },
        ],
    },
};

// ── NPC Definitions ──────────────────────────────────────────
const NPC_DEFS = {
    merlin:   { name: 'Merlin',   sprite: 'merlin',   color: '#9b59b6' },
    datadave: { name: 'DataDave', sprite: 'datadave', color: '#3498db' },
    karen:    { name: 'Karen',    sprite: 'karen',    color: '#e74c3c' },
    priya:    { name: 'Priya',    sprite: 'priya',    color: '#f39c12' },
    oracle:   { name: 'Oracle',   sprite: 'oracle',   color: '#1abc9c' },
    steve:    { name: 'Steve',    sprite: 'steve',    color: '#95a5a6' },
    boss:     { name: 'GPT-7',    sprite: 'boss',     color: '#e74c3c' },
};

// ── Item Definitions ─────────────────────────────────────────
const ITEMS = {
    rubber_duck:  { name: 'Rubber Duck',       desc: 'For debugging. Quack.', icon: {s:'base',c:23,r:9} },
    jira_ticket:  { name: 'JIRA Ticket',       desc: 'JIRA-4521: Ship the MVP', icon: {s:'base',c:20,r:0} },
    yaml_scroll:  { name: 'YAML Config Scroll', desc: 'apiVersion: v1\nkind: Chaos', icon: {s:'base',c:25,r:27} },
    api_key:      { name: 'API Key of Power',  desc: 'sk-proj-AAAA...ZZZZ', icon: {s:'base',c:24,r:27} },
    env_file:     { name: 'Sacred .env File',  desc: 'DATABASE_URL=localhost:yolo', icon: {s:'base',c:26,r:27} },
};

// ── Quest Definitions ────────────────────────────────────────
const QUEST_CHAIN = [
    { id: 'welcome',     label: 'Welcome to HypeScale',    desc: 'Talk to Karen in the office' },
    { id: 'get_yaml',    label: 'Get YAML Config Scroll',  desc: 'Find it in the conference room' },
    { id: 'get_apikey',  label: 'Get API Key of Power',    desc: 'Convince SysAdmin Steve' },
    { id: 'get_env',     label: 'Get Sacred .env File',    desc: 'Defeat GPT-7 in the dungeon' },
    { id: 'ship_it',     label: 'Ship the MVP!',           desc: 'Return to Karen' },
];

// ── Ending Text ──────────────────────────────────────────────
const ENDING_TEXT = [
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
    'DataDave still can\'t tell cats from dogs.',
    'Priya filed 847 more JIRA tickets.',
    'Steve blocked 12 more deployments.',
    'The Oracle hallucinated a new religion.',
    'GPT-7 was retrained on Reddit.',
    '',
    'And you?',
    'You shipped the MVP.',
    '',
    'That\'s all that matters.',
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
    'PRESS SPACE TO PLAY AGAIN',
];
