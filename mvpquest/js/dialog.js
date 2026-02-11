// ── Dialog System ─────────────────────────────────────────────
// Bottom-of-screen dialog box with typewriter text effect

const Dialog = {
    active: false,
    dialogId: null,
    pages: [],
    pageIndex: 0,
    displayedChars: 0,
    charTimer: 0,
    CHAR_SPEED: 0.03, // seconds per character
    callback: null,
    onEndAction: null,

    show(dialogId, callback) {
        const dialog = DIALOGS[dialogId];
        if (!dialog) return;
        this.active = true;
        this.dialogId = dialogId;
        this.pages = dialog.pages;
        this.pageIndex = 0;
        this.displayedChars = 0;
        this.charTimer = 0;
        this.callback = callback || null;
        this.onEndAction = dialog.onEnd || null;
        GameAudio.play('talk');
    },

    update(dt) {
        if (!this.active) return;
        const page = this.pages[this.pageIndex];
        if (!page) return;
        if (this.displayedChars < page.text.length) {
            this.charTimer += dt;
            while (this.charTimer >= this.CHAR_SPEED && this.displayedChars < page.text.length) {
                this.charTimer -= this.CHAR_SPEED;
                this.displayedChars++;
            }
        }
    },

    advance() {
        if (!this.active) return;
        const page = this.pages[this.pageIndex];
        if (!page) return;

        // If text still typing, show it all
        if (this.displayedChars < page.text.length) {
            this.displayedChars = page.text.length;
            return;
        }

        // Next page or close
        this.pageIndex++;
        if (this.pageIndex >= this.pages.length) {
            this.close();
        } else {
            this.displayedChars = 0;
            this.charTimer = 0;
            GameAudio.play('talk');
        }
    },

    close() {
        this.active = false;
        // Execute quest action
        if (this.onEndAction) {
            Quests.triggerAction(this.onEndAction);
        }
        if (this.callback) {
            this.callback();
        }
    },

    render(ctx, canvasW, canvasH) {
        if (!this.active) return;
        const page = this.pages[this.pageIndex];
        if (!page) return;

        const boxH = 140;
        const boxY = canvasH - boxH - 10;
        const boxX = 10;
        const boxW = canvasW - 20;

        // Semi-transparent dark box
        ctx.fillStyle = 'rgba(0, 0, 0, 0.85)';
        ctx.fillRect(boxX, boxY, boxW, boxH);

        // Border
        ctx.strokeStyle = '#fff';
        ctx.lineWidth = 2;
        ctx.strokeRect(boxX, boxY, boxW, boxH);

        // Speaker name
        if (page.speaker) {
            ctx.fillStyle = '#ffcc00';
            ctx.font = 'bold 16px monospace';
            ctx.fillText(page.speaker, boxX + 12, boxY + 22);
        }

        // Dialog text with word wrap
        ctx.fillStyle = '#ffffff';
        ctx.font = '14px monospace';
        const text = page.text.substring(0, this.displayedChars);
        const lines = this.wordWrap(text, 75);
        const textY = page.speaker ? boxY + 42 : boxY + 22;
        for (let i = 0; i < lines.length && i < 5; i++) {
            ctx.fillText(lines[i], boxX + 12, textY + i * 20);
        }

        // "Press SPACE" indicator
        if (this.displayedChars >= page.text.length) {
            ctx.fillStyle = '#aaa';
            ctx.font = '12px monospace';
            const prompt = this.pageIndex < this.pages.length - 1 ? '[ SPACE → ]' : '[ SPACE ✓ ]';
            ctx.fillText(prompt, boxX + boxW - 110, boxY + boxH - 12);
        }
    },

    wordWrap(text, maxChars) {
        const lines = [];
        for (const paragraph of text.split('\n')) {
            if (paragraph === '') { lines.push(''); continue; }
            const words = paragraph.split(' ');
            let line = '';
            for (const word of words) {
                if (line.length + word.length + 1 > maxChars) {
                    lines.push(line);
                    line = word;
                } else {
                    line = line ? line + ' ' + word : word;
                }
            }
            if (line) lines.push(line);
        }
        return lines;
    },
};
