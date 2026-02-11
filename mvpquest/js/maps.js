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
            const musicMap = { campus: 'town', office: 'office', server: 'dungeon', dungeon: 'dungeon', shrine: 'dungeon' };
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

function buildBuilding(obj, w, x, y, bw, style) {
    // style: 'beige' or 'brown'
    const B = style === 'brown' ? 'W' : 'B';
    const t = (name) => T[`BLDG_${B}_${name}`];

    // Row 0: peaked roof
    setTile(obj, w, x, y, t('PEAK_L'));
    for (let dx = 1; dx < bw - 1; dx++) setTile(obj, w, x + dx, y, t('ROOF'));
    setTile(obj, w, x + bw - 1, y, t('PEAK_R'));

    // Row 1: walls
    setTile(obj, w, x, y + 1, t('WALL_L'));
    for (let dx = 1; dx < bw - 1; dx++) setTile(obj, w, x + dx, y + 1, t('WALL'));
    setTile(obj, w, x + bw - 1, y + 1, t('WALL_R'));

    // Row 2: face (door placed separately by caller)
    setTile(obj, w, x, y + 2, t('FACE_L'));
    for (let dx = 1; dx < bw - 1; dx++) setTile(obj, w, x + dx, y + 2, t('FACE'));
    setTile(obj, w, x + bw - 1, y + 2, t('FACE_R'));
}

// ── Campus Map (30x25) ───────────────────────────────────────
function buildCampus() {
    const W = 30, H = 25;
    const ground = fillArray(W * H, T.GRASS);
    const objects = fillArray(W * H, T.NONE);

    // ── Ground variety: deterministic GRASS2 scatter (~18%) ──
    // Skip tiles under buildings, paths, and the pond
    const skipGrass = new Set();
    // Pond area (cols 3-5, rows 3-5)
    for (let sy = 3; sy <= 5; sy++)
        for (let sx = 3; sx <= 5; sx++) skipGrass.add(sy * W + sx);
    // Path tiles — vertical main (x=15, y=11-20)
    for (let sy = 11; sy <= 20; sy++) skipGrass.add(sy * W + 15);
    // Path to office (x=15-22, y=11) and door tiles
    for (let sx = 15; sx <= 22; sx++) skipGrass.add(11 * W + sx);
    skipGrass.add(10 * W + 21); skipGrass.add(10 * W + 22);
    // Path to server room (x=24, y=11-19)
    for (let sy = 11; sy <= 19; sy++) skipGrass.add(sy * W + 24);
    // Path to cave (x=4-15, y=20) + (x=4, y=20-22) + (x=3, y=22)
    for (let sx = 4; sx <= 15; sx++) skipGrass.add(20 * W + sx);
    for (let sy = 20; sy <= 22; sy++) skipGrass.add(sy * W + 4);
    skipGrass.add(22 * W + 3);
    // Path to shrine (x=8-15, y=12)
    for (let sx = 8; sx <= 15; sx++) skipGrass.add(12 * W + sx);
    // Office building (cols 19-24, rows 8-10)
    for (let sy = 8; sy <= 10; sy++)
        for (let sx = 19; sx <= 24; sx++) skipGrass.add(sy * W + sx);
    // Server room (cols 22-25, rows 17-19)
    for (let sy = 17; sy <= 19; sy++)
        for (let sx = 22; sx <= 25; sx++) skipGrass.add(sy * W + sx);
    // Shrine (cols 7-9, rows 10-12)
    for (let sy = 10; sy <= 12; sy++)
        for (let sx = 7; sx <= 9; sx++) skipGrass.add(sy * W + sx);

    for (let y = 0; y < H; y++) {
        for (let x = 0; x < W; x++) {
            if (skipGrass.has(y * W + x)) continue;
            if ((x * 7 + y * 13) % 100 < 18) {
                setTile(ground, W, x, y, T.GRASS2);
            }
        }
    }

    // ── Forest borders (2-3 trees deep, mixed pine/deciduous) ──

    // Helper: place a two-tile tree pair (canopy + trunk) on objects layer
    function placeTree(tx, ty, pine) {
        setTile(objects, W, tx, ty, pine ? T.PINE_TOP : T.TREE_TOP);
        setTile(objects, W, tx, ty + 1, pine ? T.PINE : T.TREE);
    }

    // Top border: 3 rows of trees (canopy rows 0,2; trunk rows 1,3)
    // Row 0-1: full pine row
    for (let x = 0; x < W; x++) placeTree(x, 0, true);
    // Row 2-3: mix pine and deciduous, leave gaps for things underneath
    for (let x = 0; x < W; x++) {
        // Skip cols that would overlap pond (cols 3-5 at row 3) or NPC clearance
        if (x >= 3 && x <= 5) continue; // pond area
        if (x === 6) continue; // DataDave (6,5) clearance — row 3-4 tree would block above him
        placeTree(x, 2, (x % 3 !== 0)); // every 3rd is deciduous for variety
    }

    // Bottom border: rows 21-24 (canopy at 21,23; trunk at 22,24)
    // Row 23-24: dense pines along bottom
    for (let x = 0; x < W; x++) {
        if (x >= 3 && x <= 4) continue; // cave entrance gap
        if (x === 15) continue; // player spawn clearance (15,23)
        placeTree(x, 23, true);
    }
    // Row 21-22: second row of trees, skip cave path and spawn path
    for (let x = 0; x < W; x++) {
        if (x >= 3 && x <= 5) continue; // cave path area (x=4, y=20-22)
        if (x === 15) continue; // main path at (15,20) area
        if (x >= 13 && x <= 14) continue; // clearance near main path
        if (x >= 22 && x <= 25) continue; // server room building
        placeTree(x, 21, (x % 4 !== 0)); // every 4th deciduous
    }

    // Left border: cols 0-2, rows 2 to 20 (two-tile pairs)
    // Col 0: dense pines
    for (let y = 2; y < 20; y += 2) {
        if (y >= 10 && y <= 13) continue; // shrine access gap (shrine at cols 7-9 rows 10-12)
        placeTree(0, y, true);
    }
    // Col 1: mix trees
    for (let y = 2; y < 20; y += 2) {
        if (y >= 10 && y <= 13) continue; // shrine area clearance
        placeTree(1, y, (y % 4 !== 0));
    }
    // Col 2: sparse trees to transition to open campus
    for (let y = 2; y < 18; y += 3) {
        if (y >= 8 && y <= 13) continue; // shrine area + path clearance
        if (y >= 3 && y <= 5) continue; // pond clearance
        placeTree(2, y, (y % 6 === 0));
    }

    // Right border: cols 27-29, rows 2 to 20
    // Col 29: dense pines
    for (let y = 2; y < 20; y += 2) {
        if (y === 10 || y === 11) continue; // east-west path exit at row 11
        placeTree(29, y, true);
    }
    // Col 28: mix trees
    for (let y = 2; y < 20; y += 2) {
        if (y >= 10 && y <= 12) continue; // path gap at row 11
        placeTree(28, y, (y % 4 !== 0));
    }
    // Col 27: sparse transition
    for (let y = 2; y < 18; y += 3) {
        if (y >= 8 && y <= 12) continue; // path gap + office clearance
        if (y >= 14 && y <= 16) continue; // clearance near server path area
        placeTree(27, y, (y % 6 === 0));
    }

    // ── Pond (upper-left area) — proper shore edges ──
    setTile(ground, W, 3, 3, T.WATER_TL);
    setTile(ground, W, 4, 3, T.WATER_T);
    setTile(ground, W, 5, 3, T.WATER_TR);
    setTile(ground, W, 3, 4, T.WATER_L);
    setTile(ground, W, 4, 4, T.WATER);
    setTile(ground, W, 5, 4, T.WATER_R);
    setTile(ground, W, 3, 5, T.WATER_BL);
    setTile(ground, W, 4, 5, T.WATER_B);
    setTile(ground, W, 5, 5, T.WATER_BR);

    // ── Tree groves (groups of 3-5, 1-tile clearance from doors/NPCs/paths) ──
    // Grove 1: northwest, near pond (deciduous)
    placeTree(3, 7, false);
    placeTree(4, 7, false);
    placeTree(5, 7, false);

    // Grove 2: north-center (pine cluster)
    placeTree(8, 3, true);
    placeTree(9, 3, true);
    placeTree(10, 3, true);

    // Grove 3: north-center-right (mixed)
    placeTree(15, 3, false);
    placeTree(16, 3, true);
    placeTree(17, 3, false);

    // Grove 4: northeast (deciduous cluster)
    placeTree(24, 2, false);
    placeTree(25, 2, false);
    placeTree(26, 2, true);

    // Grove 5: mid-left below shrine (mixed)
    placeTree(3, 14, false);
    placeTree(4, 14, true);
    placeTree(5, 14, false);

    // Grove 6: mid-right below office (pine)
    placeTree(23, 13, true);
    placeTree(24, 13, true);
    placeTree(25, 13, false);

    // Grove 7: southwest near cave path (deciduous)
    placeTree(7, 17, false);
    placeTree(8, 17, false);
    placeTree(9, 17, true);

    // Grove 8: south-center (pine)
    placeTree(17, 17, true);
    placeTree(18, 17, true);
    placeTree(19, 17, false);

    // Grove 9: mid-west (deciduous pair near left border transition)
    placeTree(3, 10, false);
    placeTree(4, 10, false);

    // ── Bushes (purposeful groupings near buildings/entrances) ──
    // Flanking office entrance
    setTile(objects, W, 20, 10, T.BUSH);
    setTile(objects, W, 23, 10, T.BUSH);
    // Near office north side
    setTile(objects, W, 19, 7, T.BUSH);
    setTile(objects, W, 20, 7, T.BUSH);
    // Flanking shrine entrance
    setTile(objects, W, 7, 13, T.BUSH);
    setTile(objects, W, 9, 13, T.BUSH);
    // Near server room
    setTile(objects, W, 22, 16, T.BUSH);
    setTile(objects, W, 25, 16, T.BUSH);
    // Framing open area near pond
    setTile(objects, W, 6, 3, T.BUSH);
    setTile(objects, W, 7, 3, T.BUSH);
    // Along cave path
    setTile(objects, W, 6, 19, T.BUSH);
    setTile(objects, W, 7, 19, T.BUSH);
    // Near main path middle
    setTile(objects, W, 13, 16, T.BUSH);
    setTile(objects, W, 16, 16, T.BUSH);

    // ── Flowers (~18 scattered in clearings and along paths) ──
    const flowers = [
        [5,6],[9,9],[11,11],[14,14],[8,19],[17,21],  // original 6
        [6,6],[11,7],[13,9],[16,15],[10,16],[18,14],  // near clearings
        [12,19],[19,13],[3,12],[20,5],[14,7],[7,8],   // along paths/edges
    ];
    for (const [fx,fy] of flowers) setTile(objects, W, fx, fy, T.FLOWER);

    // ── Rocks (4-5 scattered near groves and pond) ──
    setTile(objects, W, 10, 6, T.ROCK);   // original
    setTile(objects, W, 6, 5, T.ROCK);    // near pond
    setTile(objects, W, 2, 16, T.ROCK);   // near left border
    setTile(objects, W, 21, 15, T.ROCK);  // near server room area
    setTile(objects, W, 12, 8, T.ROCK);   // mid-campus

    // ── Office Building (beige, cols 19-24, rows 8-10)
    buildBuilding(objects, W, 19, 8, 6, 'beige');
    setTile(objects, W, 21, 9, T.BLDG_B_WIN_L);  // window in wall row
    setTile(objects, W, 22, 9, T.BLDG_B_WIN_R);
    setTile(objects, W, 21, 10, T.BLDG_B_DOOR_L); // door in face row
    setTile(objects, W, 22, 10, T.BLDG_B_DOOR_R);

    // ── Server Room (brown, cols 22-25, rows 17-19)
    buildBuilding(objects, W, 22, 17, 4, 'brown');
    setTile(objects, W, 24, 19, T.BLDG_W_DOOR);   // door in face row

    // ── Oracle's Shrine (beige, cols 7-9, rows 10-12)
    buildBuilding(objects, W, 7, 10, 3, 'beige');
    setTile(objects, W, 8, 12, T.BLDG_B_DOOR_L);  // door in face row

    // ── Cave Entrance (southwest area)
    setTile(objects, W, 3, 22, T.CAVE);
    setTile(objects, W, 4, 22, T.CAVE);

    // Path tiles (ground layer) from entrance to office
    for (let y = 11; y <= 20; y++) setTile(ground, W, 15, y, T.PATH);
    for (let x = 15; x <= 21; x++) setTile(ground, W, x, 11, T.PATH);
    setTile(ground, W, 21, 10, T.PATH);
    setTile(ground, W, 22, 10, T.PATH);
    // Path to server room
    for (let y = 11; y <= 19; y++) setTile(ground, W, 24, y, T.PATH);
    // Path to cave (southwest)
    for (let x = 4; x <= 15; x++) setTile(ground, W, x, 20, T.PATH);
    for (let y = 20; y <= 22; y++) setTile(ground, W, 4, y, T.PATH);
    setTile(ground, W, 3, 22, T.PATH);
    // Path to shrine
    for (let x = 8; x <= 15; x++) setTile(ground, W, x, 12, T.PATH);

    return {
        name: 'HypeScale AI Campus',
        width: W, height: H,
        ground, objects,
        playerStart: { x: 15, y: 23 },
        transitions: [
            { x: 21, y: 10, target: 'office', tx: 9, ty: 13 },
            { x: 22, y: 10, target: 'office', tx: 10, ty: 13 },
            { x: 24, y: 19, target: 'server', tx: 5, ty: 8 },
            { x: 8,  y: 12, target: 'shrine', tx: 4, ty: 5 },
            { x: 3,  y: 22, target: 'dungeon', tx: 1, ty: 1 },
            { x: 4,  y: 22, target: 'dungeon', tx: 2, ty: 1 },
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
            { x: 1, y: 0, target: 'campus', tx: 3, ty: 21 },
            { x: 2, y: 0, target: 'campus', tx: 4, ty: 21 },
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

// ── Oracle's Shrine (9x7) ────────────────────────────────────
function buildShrine() {
    const W = 9, H = 7;
    const ground = fillArray(W * H, T.FLOOR_W);
    const objects = fillArray(W * H, T.NONE);

    // Outer walls
    buildWallBox(objects, W, 0, 0, W, H, {
        t: T.WALL_I_T, f: T.WALL_I_F,
        tl: T.WALL_I_TL, tr: T.WALL_I_TR,
        bl: T.WALL_I_BL, br: T.WALL_I_BR,
        l: T.WALL_I_L, r: T.WALL_I_R, b: T.WALL_I_B,
    });

    // Pedestal behind the Oracle
    setTile(objects, W, 4, 2, T.PEDESTAL);

    // Pillars flanking the room
    setTile(objects, W, 2, 2, T.PILLAR);
    setTile(objects, W, 6, 2, T.PILLAR);

    // Candle-like decor (plants) along the walls
    setTile(objects, W, 1, 1, T.PLANT_I);
    setTile(objects, W, 7, 1, T.PLANT_I);
    setTile(objects, W, 1, 5, T.PLANT_I);
    setTile(objects, W, 7, 5, T.PLANT_I);

    // Door back to campus (south wall center)
    setTile(objects, W, 4, H - 1, T.DOOR_INT);

    return {
        name: 'The Oracle\'s Shrine',
        width: W, height: H,
        ground, objects,
        playerStart: { x: 4, y: 5 },
        transitions: [
            { x: 4, y: H - 1, target: 'campus', tx: 8, ty: 13 },
        ],
        npcs: [
            { id: 'oracle', x: 4, y: 3, def: NPC_DEFS.oracle },
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
    shrine:  buildShrine(),
};
