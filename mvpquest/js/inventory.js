// ── Inventory System ──────────────────────────────────────────
// Item collection, storage, and overlay UI

const Inventory = {
    items: [],
    visible: false,

    add(itemId) {
        if (!this.has(itemId)) {
            this.items.push(itemId);
            GameAudio.play('item');
        }
    },

    has(itemId) {
        return this.items.includes(itemId);
    },

    toggle() {
        this.visible = !this.visible;
    },

    render(ctx, canvasW, canvasH) {
        if (!this.visible) return;

        // Overlay background
        ctx.fillStyle = 'rgba(0, 0, 0, 0.8)';
        ctx.fillRect(40, 40, canvasW - 80, canvasH - 80);

        // Border
        ctx.strokeStyle = '#ffcc00';
        ctx.lineWidth = 2;
        ctx.strokeRect(40, 40, canvasW - 80, canvasH - 80);

        // Title
        ctx.fillStyle = '#ffcc00';
        ctx.font = 'bold 20px monospace';
        ctx.fillText('INVENTORY', 60, 72);

        // Items
        ctx.font = '14px monospace';
        if (this.items.length === 0) {
            ctx.fillStyle = '#888';
            ctx.fillText('Empty... go find some artifacts!', 60, 110);
        } else {
            for (let i = 0; i < this.items.length; i++) {
                const item = ITEMS[this.items[i]];
                if (!item) continue;
                const y = 100 + i * 60;

                // Draw item icon
                if (item.icon) {
                    Sprites.drawSprite(ctx, item.icon.s, item.icon.c, item.icon.r, 60, y, 2);
                }

                // Item name
                ctx.fillStyle = '#fff';
                ctx.font = 'bold 14px monospace';
                ctx.fillText(item.name, 100, y + 14);

                // Item description
                ctx.fillStyle = '#aaa';
                ctx.font = '12px monospace';
                ctx.fillText(item.desc, 100, y + 30);
            }
        }

        // Close hint
        ctx.fillStyle = '#888';
        ctx.font = '12px monospace';
        ctx.fillText('Press I or ESC to close', 60, canvasH - 60);
    },

    // Show a brief pickup notification
    showPickup(itemId) {
        this.pickupNotif = { id: itemId, timer: 2.0 };
    },

    updateNotif(dt) {
        if (this.pickupNotif) {
            this.pickupNotif.timer -= dt;
            if (this.pickupNotif.timer <= 0) this.pickupNotif = null;
        }
    },

    renderNotif(ctx, canvasW) {
        if (!this.pickupNotif) return;
        const item = ITEMS[this.pickupNotif.id];
        if (!item) return;

        const alpha = Math.min(1, this.pickupNotif.timer);
        ctx.globalAlpha = alpha;
        ctx.fillStyle = 'rgba(0, 100, 0, 0.9)';
        ctx.fillRect(canvasW / 2 - 150, 10, 300, 36);
        ctx.strokeStyle = '#0f0';
        ctx.lineWidth = 1;
        ctx.strokeRect(canvasW / 2 - 150, 10, 300, 36);
        ctx.fillStyle = '#fff';
        ctx.font = 'bold 14px monospace';
        ctx.textAlign = 'center';
        ctx.fillText('Got: ' + item.name + '!', canvasW / 2, 33);
        ctx.textAlign = 'left';
        ctx.globalAlpha = 1;
    },
};
