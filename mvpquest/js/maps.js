// ── Map System ────────────────────────────────────────────────
// Map data, rendering, collision, transitions

const Maps = {
    current: null,
    currentId: null,
    fadeAlpha: 0,
    fading: false,
    fadeCallback: null,

    TILE_SIZE: 16,
    SCALE: 3,
    RENDER_SIZE: 48, // 16 * 3

    load(mapId) {
        this.currentId = mapId;
        this.current = MAP_DATA[mapId];
    },

    getTile(layer, x, y) {
        if (!this.current) return T.NONE;
        if (x < 0 || y < 0 || x >= this.current.width || y >= this.current.height) return T.WALL_F;
        return this.current[layer][y * this.current.width + x];
    },

    isBlocked(x, y) {
        if (!this.current) return true;
        if (x < 0 || y < 0 || x >= this.current.width || y >= this.current.height) return true;
        const groundTile = this.current.ground[y * this.current.width + x];
        const objTile = this.current.objects[y * this.current.width + x];
        return BLOCKING_TILES.has(groundTile) || BLOCKING_TILES.has(objTile);
    },

    getTransition(x, y) {
        if (!this.current || !this.current.transitions) return null;
        for (const t of this.current.transitions) {
            if (t.x === x && t.y === y) return t;
        }
        return null;
    },

    render(ctx, camX, camY, viewW, viewH) {
        if (!this.current) return;
        const rs = this.RENDER_SIZE;
        const startCol = Math.max(0, Math.floor(camX / rs));
        const startRow = Math.max(0, Math.floor(camY / rs));
        const endCol = Math.min(this.current.width, Math.ceil((camX + viewW) / rs) + 1);
        const endRow = Math.min(this.current.height, Math.ceil((camY + viewH) / rs) + 1);

        for (let row = startRow; row < endRow; row++) {
            for (let col = startCol; col < endCol; col++) {
                const dx = col * rs - camX;
                const dy = row * rs - camY;
                const idx = row * this.current.width + col;

                // Ground layer
                const gTile = this.current.ground[idx];
                if (gTile !== T.NONE) {
                    Sprites.drawTile(ctx, gTile, dx, dy);
                }

                // Objects layer
                const oTile = this.current.objects[idx];
                if (oTile !== T.NONE) {
                    Sprites.drawTile(ctx, oTile, dx, dy);
                }
            }
        }
    },

    // Fade transition between maps
    startTransition(targetMap, targetX, targetY) {
        this.fading = true;
        this.fadeAlpha = 0;
        this.fadeCallback = () => {
            this.load(targetMap);
            Entities.player.x = targetX;
            Entities.player.y = targetY;
            Entities.loadMapEntities(targetMap);
            // Play appropriate music
            const musicMap = { campus: 'town', office: 'office', server: 'dungeon', dungeon: 'dungeon' };
            GameAudio.playMusic(musicMap[targetMap] || 'town');
        };
    },

    updateFade(dt) {
        if (!this.fading) return;
        if (this.fadeAlpha < 1 && this.fadeCallback) {
            this.fadeAlpha = Math.min(1, this.fadeAlpha + dt * 3);
            if (this.fadeAlpha >= 1) {
                this.fadeCallback();
                this.fadeCallback = null;
            }
        } else if (!this.fadeCallback) {
            this.fadeAlpha = Math.max(0, this.fadeAlpha - dt * 3);
            if (this.fadeAlpha <= 0) {
                this.fading = false;
            }
        }
    },

    renderFade(ctx, w, h) {
        if (this.fadeAlpha > 0) {
            ctx.fillStyle = `rgba(0,0,0,${this.fadeAlpha})`;
            ctx.fillRect(0, 0, w, h);
        }
    },
};

// ── Map Data Builder Helpers ──────────────────────────────────

function fillArray(size, val) { return new Array(size).fill(val); }

function setTile(arr, w, x, y, tile) { arr[y * w + x] = tile; }

function fillRect(arr, w, x, y, rw, rh, tile) {
    for (let dy = 0; dy < rh; dy++)
        for (let dx = 0; dx < rw; dx++)
            setTile(arr, w, x + dx, y + dy, tile);
}

function buildWallBox(obj, w, x, y, bw, bh, tiles) {
    // tiles: { t, f, tl, tr, bl, br, l, r, b }
    // Falls back to original 2-tile behavior when only t/f are given
    const tl = tiles.tl || tiles.t;
    const tr = tiles.tr || tiles.t;
    const bl = tiles.bl || tiles.f;
    const br = tiles.br || tiles.f;
    const l  = tiles.l  || tiles.f;
    const r  = tiles.r  || tiles.f;
    const b  = tiles.b  || tiles.f;

    // Corners
    setTile(obj, w, x, y, tl);
    setTile(obj, w, x + bw - 1, y, tr);
    setTile(obj, w, x, y + bh - 1, bl);
    setTile(obj, w, x + bw - 1, y + bh - 1, br);

    // Top edge (between corners)
    for (let dx = 1; dx < bw - 1; dx++) setTile(obj, w, x + dx, y, tiles.t);
    // Bottom edge (between corners)
    for (let dx = 1; dx < bw - 1; dx++) setTile(obj, w, x + dx, y + bh - 1, b);
    // Left edge (between corners)
    for (let dy = 1; dy < bh - 1; dy++) setTile(obj, w, x, y + dy, l);
    // Right edge (between corners)
    for (let dy = 1; dy < bh - 1; dy++) setTile(obj, w, x + bw - 1, y + dy, r);
}

// ── Campus Map (30x25) ───────────────────────────────────────
function buildCampus() {
    const W = 30, H = 25;
    const ground = fillArray(W * H, T.GRASS);
    const objects = fillArray(W * H, T.NONE);

    // Tree border — two-tile-tall pines (canopy + trunk)
    // Top border: canopy at row 0, trunk at row 1
    for (let x = 0; x < W; x++) {
        setTile(objects, W, x, 0, T.PINE_TOP);
        setTile(objects, W, x, 1, T.PINE);
    }
    // Bottom border: canopy at H-2, trunk at H-1 (skip path/entrance cols 14-16)
    for (let x = 0; x < W; x++) {
        if (x >= 14 && x <= 16) continue; // leave gap for path + cave entrance
        setTile(objects, W, x, H-2, T.PINE_TOP);
        setTile(objects, W, x, H-1, T.PINE);
    }
    // Left + right borders: two-tile-tall pines every other row
    for (let y = 2; y < H - 3; y += 2) {
        setTile(objects, W, 0, y, T.PINE_TOP);
        setTile(objects, W, 0, y + 1, T.PINE);
        setTile(objects, W, W-1, y, T.PINE_TOP);
        setTile(objects, W, W-1, y + 1, T.PINE);
    }

    // Pond (upper-left area) — proper shore edges
    // Row 3 (top): TL, T, TR
    setTile(ground, W, 3, 3, T.WATER_TL);
    setTile(ground, W, 4, 3, T.WATER_T);
    setTile(ground, W, 5, 3, T.WATER_TR);
    // Row 4 (middle): L, center, R
    setTile(ground, W, 3, 4, T.WATER_L);
    setTile(ground, W, 4, 4, T.WATER);
    setTile(ground, W, 5, 4, T.WATER_R);
    // Row 5 (bottom): BL, B, BR
    setTile(ground, W, 3, 5, T.WATER_BL);
    setTile(ground, W, 4, 5, T.WATER_B);
    setTile(ground, W, 5, 5, T.WATER_BR);

    // Scattered trees — two-tile-tall (canopy at y, trunk at y+1)
    const treeTops = [[3,7],[4,7],[2,9],[8,3],[9,3],[15,3],[16,3],
                      [25,2],[26,2],[7,14],[8,14],[23,14],[24,14],
                      [3,17],[4,17],[12,19],[27,7]];
    for (const [tx,ty] of treeTops) {
        setTile(objects, W, tx, ty, T.TREE_TOP);
        setTile(objects, W, tx, ty + 1, T.TREE);
    }

    // Bushes
    const bushes = [[6,4],[7,4],[2,13],[5,10],[20,3],[21,3],[13,18],[14,18],[20,20],[21,20]];
    for (const [bx,by] of bushes) setTile(objects, W, bx, by, T.BUSH);

    // Flowers (non-blocking ground decorations)
    const flowers = [[5,6],[9,9],[11,11],[14,14],[8,19],[17,21]];
    for (const [fx,fy] of flowers) setTile(objects, W, fx, fy, T.FLOWER);

    // Rocks
    setTile(objects, W, 10, 6, T.ROCK);
    setTile(objects, W, 22, 17, T.ROCK);

    // ── Office Building (upper-right: cols 17-26, rows 4-10)
    buildWallBox(objects, W, 17, 4, 10, 7, { t: T.WALL_T, f: T.WALL_F });
    // Door on south face
    setTile(objects, W, 21, 10, T.DOOR_EXT);
    setTile(objects, W, 22, 10, T.DOOR_EXT);

    // ── Server Room (lower-right: cols 22-27, rows 16-19)
    buildWallBox(objects, W, 22, 16, 6, 4, { t: T.WALL_T, f: T.WALL_F });
    // Door on south face
    setTile(objects, W, 24, 19, T.DOOR_EXT);

    // ── Cave Entrance (lower area)
    setTile(objects, W, 14, 22, T.CAVE);
    setTile(objects, W, 15, 22, T.CAVE);

    // Path tiles (ground layer) from entrance to office
    for (let y = 11; y <= 23; y++) setTile(ground, W, 15, y, T.PATH);
    for (let x = 15; x <= 21; x++) setTile(ground, W, x, 11, T.PATH);
    setTile(ground, W, 21, 10, T.PATH);
    setTile(ground, W, 22, 10, T.PATH);
    // Path to server room
    for (let y = 11; y <= 19; y++) setTile(ground, W, 24, y, T.PATH);
    // Path to cave
    for (let x = 14; x <= 15; x++) setTile(ground, W, x, 22, T.PATH);
    for (let y = 21; y <= 22; y++) setTile(ground, W, 15, y, T.PATH);

    return {
        name: 'HypeScale AI Campus',
        width: W, height: H,
        ground, objects,
        playerStart: { x: 15, y: 23 },
        transitions: [
            { x: 21, y: 10, target: 'office', tx: 9, ty: 13 },
            { x: 22, y: 10, target: 'office', tx: 10, ty: 13 },
            { x: 24, y: 19, target: 'server', tx: 5, ty: 8 },
            { x: 14, y: 22, target: 'dungeon', tx: 1, ty: 1 },
            { x: 15, y: 22, target: 'dungeon', tx: 2, ty: 1 },
        ],
        npcs: [
            { id: 'merlin',   x: 12, y: 12, def: NPC_DEFS.merlin },
            { id: 'datadave', x: 6,  y: 5,  def: NPC_DEFS.datadave },
        ],
        music: 'town',
    };
}

// ── Office Map (20x15) ──────────────────────────────────────
function buildOffice() {
    const W = 20, H = 15;
    const ground = fillArray(W * H, T.FLOOR_W);
    const objects = fillArray(W * H, T.NONE);

    // Outer walls
    buildWallBox(objects, W, 0, 0, W, H, {
        t: T.WALL_I_T, f: T.WALL_I_F,
        tl: T.WALL_I_TL, tr: T.WALL_I_TR,
        bl: T.WALL_I_BL, br: T.WALL_I_BR,
        l: T.WALL_I_L, r: T.WALL_I_R, b: T.WALL_I_B,
    });

    // ── Karen's Office (top-right room: cols 12-19, rows 0-6)
    // Horizontal divider wall at row 6 (left junction to right outer wall)
    setTile(objects, W, 12, 6, T.WALL_I_TL);         // left T-junction uses corner
    for (let dx = 13; dx < W - 1; dx++) setTile(objects, W, dx, 6, T.WALL_I_T);
    setTile(objects, W, W - 1, 6, T.WALL_I_R);       // meets right outer wall
    setTile(objects, W, 13, 6, T.DOOR_INT);           // door
    // Karen's desk
    setTile(objects, W, 16, 2, T.DESK);
    setTile(objects, W, 17, 2, T.DESK);
    setTile(objects, W, 16, 3, T.CHAIR);

    // ── Conference Room (top-left: cols 0-10, rows 0-6)
    // Vertical divider wall at col 10 (top outer wall down to row 6)
    setTile(objects, W, 10, 0, T.WALL_I_T);           // meets top outer wall
    for (let dy = 1; dy < 6; dy++) setTile(objects, W, 10, dy, T.WALL_I_R);
    setTile(objects, W, 10, 6, T.WALL_I_BR);          // corner where dividers meet
    setTile(objects, W, 10, 5, T.DOOR_INT);            // door
    // Conference table
    fillRect(objects, W, 3, 2, 4, 2, T.TABLE);
    // YAML Scroll on table
    setTile(objects, W, 5, 3, T.SCROLL_OBJ);

    // ── Main area (bottom half: rows 7-14)
    // Desks
    setTile(objects, W, 2, 8, T.DESK);
    setTile(objects, W, 2, 9, T.CHAIR);
    setTile(objects, W, 5, 8, T.DESK);
    setTile(objects, W, 5, 9, T.CHAIR);
    setTile(objects, W, 8, 8, T.DESK);
    setTile(objects, W, 8, 9, T.CHAIR);

    // Bookshelves along walls
    setTile(objects, W, 1, 8, T.SHELF);
    setTile(objects, W, 1, 10, T.SHELF);
    setTile(objects, W, 18, 8, T.SHELF);
    setTile(objects, W, 18, 10, T.SHELF);

    // Plants
    setTile(objects, W, 1, 12, T.PLANT_I);
    setTile(objects, W, 18, 12, T.PLANT_I);

    // Door back to campus (south wall)
    setTile(objects, W, 9, H-1, T.DOOR_INT);
    setTile(objects, W, 10, H-1, T.DOOR_INT);

    return {
        name: 'Office Interior',
        width: W, height: H,
        ground, objects,
        playerStart: { x: 9, y: 13 },
        transitions: [
            { x: 9,  y: H-1, target: 'campus', tx: 21, ty: 11 },
            { x: 10, y: H-1, target: 'campus', tx: 22, ty: 11 },
        ],
        npcs: [
            { id: 'karen',  x: 15, y: 3,  def: NPC_DEFS.karen },
            { id: 'priya',  x: 3,  y: 9,  def: NPC_DEFS.priya },
            { id: 'oracle', x: 12, y: 10, def: NPC_DEFS.oracle },
        ],
        items: [
            { id: 'yaml_scroll', x: 5, y: 4, dialog: 'yaml_pickup' },
        ],
        music: 'office',
    };
}

// ── Server Room (12x10) ─────────────────────────────────────
function buildServer() {
    const W = 12, H = 10;
    const ground = fillArray(W * H, T.STONE_F);
    const objects = fillArray(W * H, T.NONE);

    // Walls
    buildWallBox(objects, W, 0, 0, W, H, {
        t: T.STONE_W_T, f: T.STONE_W_F,
        tl: T.STONE_W_TL, tr: T.STONE_W_TR,
        bl: T.STONE_W_BL, br: T.STONE_W_BR,
        l: T.STONE_W_L, r: T.STONE_W_R, b: T.STONE_W_B,
    });

    // Server racks along walls
    for (let x = 2; x <= 9; x += 2) {
        setTile(objects, W, x, 1, T.RACK);
    }
    setTile(objects, W, 1, 3, T.RACK);
    setTile(objects, W, 1, 5, T.RACK);
    setTile(objects, W, 10, 3, T.RACK);
    setTile(objects, W, 10, 5, T.RACK);

    // API Key pedestal in center
    setTile(objects, W, 5, 4, T.PEDESTAL);
    setTile(objects, W, 6, 4, T.PEDESTAL);

    // Terminal
    setTile(objects, W, 3, 7, T.TERMINAL);

    // Door back to campus
    setTile(objects, W, 5, H-1, T.DOOR_INT);

    return {
        name: 'Server Room',
        width: W, height: H,
        ground, objects,
        playerStart: { x: 5, y: 8 },
        transitions: [
            { x: 5, y: H-1, target: 'campus', tx: 24, ty: 20 },
        ],
        npcs: [
            { id: 'steve', x: 4, y: 5, def: NPC_DEFS.steve },
        ],
        music: 'dungeon',
    };
}

// ── Legacy Codebase Dungeon (25x20) ─────────────────────────
function buildDungeon() {
    const W = 25, H = 20;
    const ground = fillArray(W * H, T.STONE_F);
    const objects = fillArray(W * H, T.NONE);

    // Fill everything with walls, then carve corridors
    fillRect(objects, W, 0, 0, W, H, T.STONE_W_F);

    // Carve entrance corridor (top-left)
    fillRect(objects, W, 1, 1, 3, 3, T.NONE);

    // Carve main horizontal corridor
    fillRect(objects, W, 1, 2, 15, 2, T.NONE);

    // Carve vertical corridor down
    fillRect(objects, W, 13, 2, 2, 10, T.NONE);

    // Carve horizontal corridor east
    fillRect(objects, W, 13, 10, 10, 2, T.NONE);

    // Carve corridor south
    fillRect(objects, W, 21, 10, 2, 6, T.NONE);

    // Carve corridor west to boss room
    fillRect(objects, W, 10, 14, 13, 2, T.NONE);

    // Boss room (bottom-left area)
    fillRect(objects, W, 2, 13, 8, 6, T.NONE);

    // Side rooms / dead ends
    fillRect(objects, W, 4, 4, 4, 3, T.NONE); // small room
    fillRect(objects, W, 17, 4, 5, 4, T.NONE); // side room

    // Connect side rooms
    fillRect(objects, W, 6, 3, 2, 2, T.NONE);
    fillRect(objects, W, 17, 7, 2, 4, T.NONE);

    // Pillars for atmosphere
    setTile(objects, W, 3, 15, T.PILLAR);
    setTile(objects, W, 8, 15, T.PILLAR);
    setTile(objects, W, 15, 3, T.PILLAR);
    setTile(objects, W, 19, 6, T.PILLAR);

    // Exit door (top: back to campus)
    setTile(objects, W, 1, 0, T.DOOR_INT);
    setTile(objects, W, 2, 0, T.DOOR_INT);

    return {
        name: 'The Legacy Codebase',
        width: W, height: H,
        ground, objects,
        playerStart: { x: 1, y: 1 },
        transitions: [
            { x: 1, y: 0, target: 'campus', tx: 14, ty: 21 },
            { x: 2, y: 0, target: 'campus', tx: 15, ty: 21 },
        ],
        npcs: [
            { id: 'boss', x: 5, y: 15, def: NPC_DEFS.boss },
        ],
        enemies: [
            { x: 10, y: 2, patrolAxis: 'x', patrolMin: 8, patrolMax: 12, speed: 1.5 },
            { x: 13, y: 6, patrolAxis: 'y', patrolMin: 4, patrolMax: 9, speed: 1.2 },
            { x: 19, y: 11, patrolAxis: 'x', patrolMin: 15, patrolMax: 21, speed: 1.8 },
            { x: 15, y: 14, patrolAxis: 'x', patrolMin: 12, patrolMax: 20, speed: 1.0 },
        ],
        music: 'dungeon',
    };
}

// ── Build All Maps ───────────────────────────────────────────
const MAP_DATA = {
    campus:  buildCampus(),
    office:  buildOffice(),
    server:  buildServer(),
    dungeon: buildDungeon(),
};
