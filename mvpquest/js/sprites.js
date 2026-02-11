// ── Sprite System ─────────────────────────────────────────────
// Loads Kenney roguelike spritesheets and draws tiles

const Sprites = {
    sheets: {},
    loaded: false,

    load(callback) {
        const defs = {
            base:    'assets/2D assets/Roguelike Base Pack/Spritesheet/roguelikeSheet_transparent.png',
            chars:   'assets/2D assets/Roguelike Characters Pack/Spritesheet/roguelikeChar_transparent.png',
            indoor:  'assets/2D assets/Roguelike Interior Pack/Tilesheets/roguelikeIndoor_transparent.png',
            dungeon: 'assets/2D assets/Roguelike Dungeon Pack/Spritesheet/roguelikeDungeon_transparent.png',
            city:    'assets/2D assets/Roguelike City Pack/Tilemap/tilemap.png',
        };
        const keys = Object.keys(defs);
        let count = 0;
        for (const key of keys) {
            const img = new Image();
            img.onload = () => {
                this.sheets[key] = img;
                count++;
                if (count === keys.length) {
                    this.loaded = true;
                    callback();
                }
            };
            img.onerror = () => {
                console.warn('Failed to load sheet:', key, defs[key]);
                count++;
                if (count === keys.length) {
                    this.loaded = true;
                    callback();
                }
            };
            img.src = defs[key];
        }
    },

    // Draw a tile from a spritesheet at (col, row) to canvas position (dx, dy)
    // Uses 17px stride (16px tile + 1px margin)
    drawSprite(ctx, sheetName, col, row, dx, dy, scale) {
        const sheet = this.sheets[sheetName];
        if (!sheet) return;
        const sx = col * 17;
        const sy = row * 17;
        const size = 16 * (scale || 3);
        ctx.drawImage(sheet, sx, sy, 16, 16, dx, dy, size, size);
    },

    // Draw a map tile by tile ID
    drawTile(ctx, tileId, dx, dy, scale) {
        const def = TILE_ATLAS[tileId];
        if (!def) return;
        this.drawSprite(ctx, def.s, def.c, def.r, dx, dy, scale);
    },

    // Draw a character (body + outfit layers)
    drawCharacter(ctx, spriteKey, dx, dy, scale) {
        const charDef = CHAR_SPRITES[spriteKey];
        if (!charDef) return;
        // Draw body layer
        this.drawSprite(ctx, 'chars', charDef.body.c, charDef.body.r, dx, dy, scale);
        // Draw outfit layer on top
        this.drawSprite(ctx, 'chars', charDef.outfit.c, charDef.outfit.r, dx, dy, scale);
    },
};
