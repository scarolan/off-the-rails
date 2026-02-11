// ── Entity System ─────────────────────────────────────────────
// Player, NPCs, enemies

const Entities = {
    player: { x: 0, y: 0, dir: 'down', moveTimer: 0 },
    npcs: [],
    enemies: [],
    mapItems: [],
    MOVE_COOLDOWN: 0.15,

    loadMapEntities(mapId) {
        const map = MAP_DATA[mapId];
        if (!map) return;

        // Load NPCs
        this.npcs = (map.npcs || []).map(n => ({
            ...n,
            sprite: n.def.sprite,
            name: n.def.name,
            color: n.def.color,
        }));

        // Load enemies
        this.enemies = (map.enemies || []).map(e => ({
            ...e,
            pos: e.patrolAxis === 'x' ? e.x : e.y,
            dir: 1,
        }));

        // Load items (only if not already picked up)
        this.mapItems = (map.items || []).filter(i => !Inventory.has(i.id)).map(i => ({...i}));
    },

    update(dt) {
        // Update move cooldown
        if (this.player.moveTimer > 0) {
            this.player.moveTimer -= dt;
        }

        // Update enemies
        for (const enemy of this.enemies) {
            const speed = enemy.speed * dt;
            enemy.pos += speed * enemy.dir;
            if (enemy.pos >= enemy.patrolMax) { enemy.pos = enemy.patrolMax; enemy.dir = -1; }
            if (enemy.pos <= enemy.patrolMin) { enemy.pos = enemy.patrolMin; enemy.dir = 1; }
            // Update actual position
            if (enemy.patrolAxis === 'x') {
                enemy.x = Math.round(enemy.pos);
            } else {
                enemy.y = Math.round(enemy.pos);
            }
        }

        // Check enemy collision with player
        for (const enemy of this.enemies) {
            if (enemy.x === this.player.x && enemy.y === this.player.y) {
                this.enemyHit();
            }
        }
    },

    enemyHit() {
        // Reset player to map entrance
        GameAudio.play('error');
        const map = Maps.current;
        if (map && map.playerStart) {
            this.player.x = map.playerStart.x;
            this.player.y = map.playerStart.y;
        }
    },

    tryMove(dx, dy) {
        if (this.player.moveTimer > 0) return false;

        // Update direction
        if (dx > 0) this.player.dir = 'right';
        else if (dx < 0) this.player.dir = 'left';
        else if (dy > 0) this.player.dir = 'down';
        else if (dy < 0) this.player.dir = 'up';

        const newX = this.player.x + dx;
        const newY = this.player.y + dy;

        // Check NPC collision (NPCs block movement)
        for (const npc of this.npcs) {
            if (npc.x === newX && npc.y === newY) {
                this.player.moveTimer = this.MOVE_COOLDOWN;
                return false;
            }
        }

        // Check map collision
        if (Maps.isBlocked(newX, newY)) {
            return false;
        }

        // Move player
        this.player.x = newX;
        this.player.y = newY;
        this.player.moveTimer = this.MOVE_COOLDOWN;
        GameAudio.playFootstep();

        // Check transitions
        const transition = Maps.getTransition(newX, newY);
        if (transition) {
            GameAudio.play('door');
            Maps.startTransition(transition.target, transition.tx, transition.ty);
            return true;
        }

        // Check item pickups
        for (let i = this.mapItems.length - 1; i >= 0; i--) {
            const item = this.mapItems[i];
            if (item.x === newX && item.y === newY) {
                if (item.dialog) {
                    Dialog.show(item.dialog);
                } else {
                    Inventory.add(item.id);
                    Inventory.showPickup(item.id);
                }
                this.mapItems.splice(i, 1);
            }
        }

        return true;
    },

    interact() {
        // Check for NPC in the direction player is facing
        let targetX = this.player.x;
        let targetY = this.player.y;
        switch (this.player.dir) {
            case 'up':    targetY--; break;
            case 'down':  targetY++; break;
            case 'left':  targetX--; break;
            case 'right': targetX++; break;
        }

        // Find NPC at target position
        for (const npc of this.npcs) {
            if (npc.x === targetX && npc.y === targetY) {
                const dialogId = Quests.getDialog(npc.id);
                if (dialogId) {
                    Dialog.show(dialogId);
                }
                return true;
            }
        }

        // Check for items at target position
        for (let i = this.mapItems.length - 1; i >= 0; i--) {
            const item = this.mapItems[i];
            if (item.x === targetX && item.y === targetY) {
                if (item.dialog) {
                    Dialog.show(item.dialog);
                } else {
                    Inventory.add(item.id);
                    Inventory.showPickup(item.id);
                }
                this.mapItems.splice(i, 1);
                return true;
            }
        }

        return false;
    },

    render(ctx, camX, camY) {
        const rs = Maps.RENDER_SIZE;

        // Render map items
        for (const item of this.mapItems) {
            const dx = item.x * rs - camX;
            const dy = item.y * rs - camY;
            // Draw a glowing effect
            ctx.fillStyle = 'rgba(255, 255, 100, 0.3)';
            ctx.fillRect(dx + 8, dy + 8, rs - 16, rs - 16);
            // Draw item icon if defined
            const itemDef = ITEMS[item.id];
            if (itemDef && itemDef.icon) {
                Sprites.drawSprite(ctx, itemDef.icon.s, itemDef.icon.c, itemDef.icon.r, dx, dy);
            }
        }

        // Render enemies
        for (const enemy of this.enemies) {
            const dx = enemy.x * rs - camX;
            const dy = enemy.y * rs - camY;
            // Draw bug enemy as a red/orange creature
            ctx.fillStyle = '#e74c3c';
            ctx.fillRect(dx + 8, dy + 8, rs - 16, rs - 16);
            // Bug "body"
            ctx.fillStyle = '#c0392b';
            ctx.fillRect(dx + 12, dy + 12, rs - 24, rs - 24);
            // Eyes
            ctx.fillStyle = '#fff';
            ctx.fillRect(dx + 14, dy + 14, 6, 6);
            ctx.fillRect(dx + 28, dy + 14, 6, 6);
            ctx.fillStyle = '#000';
            ctx.fillRect(dx + 16, dy + 16, 3, 3);
            ctx.fillRect(dx + 30, dy + 16, 3, 3);
            // Label
            ctx.fillStyle = '#ff6';
            ctx.font = '10px monospace';
            ctx.textAlign = 'center';
            ctx.fillText('BUG', dx + rs/2, dy + 4);
            ctx.textAlign = 'left';
        }

        // Render NPCs
        for (const npc of this.npcs) {
            const dx = npc.x * rs - camX;
            const dy = npc.y * rs - camY;
            // Draw character sprite
            Sprites.drawCharacter(ctx, npc.sprite, dx, dy);
            // Draw name tag
            ctx.fillStyle = npc.color || '#fff';
            ctx.font = 'bold 10px monospace';
            ctx.textAlign = 'center';
            ctx.fillText(npc.name, dx + rs/2, dy - 4);
            ctx.textAlign = 'left';
        }

        // Render player
        const px = this.player.x * rs - camX;
        const py = this.player.y * rs - camY;
        Sprites.drawCharacter(ctx, 'player', px, py);

        // Direction indicator (small triangle)
        ctx.fillStyle = '#fff';
        const cx = px + rs/2;
        const cy = py + rs/2;
        ctx.beginPath();
        switch (this.player.dir) {
            case 'up':    ctx.moveTo(cx, py-2); ctx.lineTo(cx-4, py+4); ctx.lineTo(cx+4, py+4); break;
            case 'down':  ctx.moveTo(cx, py+rs+2); ctx.lineTo(cx-4, py+rs-4); ctx.lineTo(cx+4, py+rs-4); break;
            case 'left':  ctx.moveTo(px-2, cy); ctx.lineTo(px+4, cy-4); ctx.lineTo(px+4, cy+4); break;
            case 'right': ctx.moveTo(px+rs+2, cy); ctx.lineTo(px+rs-4, cy-4); ctx.lineTo(px+rs-4, cy+4); break;
        }
        ctx.fill();
    },
};
