// ── Game Engine ───────────────────────────────────────────────
// Main loop, state machine, input handling, camera

const Engine = {
    canvas: null,
    ctx: null,
    WIDTH: 720,
    HEIGHT: 480,
    state: 'loading', // loading | title | playing | dialog | inventory | ending

    // Camera
    camX: 0,
    camY: 0,

    // Input
    keys: {},
    justPressed: {},

    // Ending
    endingScroll: 0,
    endingSpeed: 30, // pixels per second

    // Title screen
    titleBlink: 0,

    init() {
        this.canvas = document.getElementById('game');
        this.canvas.width = this.WIDTH;
        this.canvas.height = this.HEIGHT;
        this.ctx = this.canvas.getContext('2d');
        this.ctx.imageSmoothingEnabled = false;

        // Input listeners
        window.addEventListener('keydown', (e) => {
            if (!this.keys[e.code]) {
                this.justPressed[e.code] = true;
            }
            this.keys[e.code] = true;
            // Prevent scrolling
            if (['ArrowUp','ArrowDown','ArrowLeft','ArrowRight','Space'].includes(e.code)) {
                e.preventDefault();
            }
        });
        window.addEventListener('keyup', (e) => {
            this.keys[e.code] = false;
        });

        // Load assets
        this.state = 'loading';
        Sprites.load(() => {
            GameAudio.load(() => {
                this.startTitle();
            });
        });
    },

    startTitle() {
        this.state = 'title';
        this.titleBlink = 0;
    },

    startGame() {
        this.state = 'playing';
        Maps.load('campus');
        const start = Maps.current.playerStart;
        Entities.player.x = start.x;
        Entities.player.y = start.y;
        Entities.loadMapEntities('campus');
        GameAudio.playMusic('town');

        // Reset quest state
        Quests.flags = {};
        Quests.currentStep = 0;
        Quests.questStarted = false;
        Inventory.items = [];
    },

    startEnding() {
        this.state = 'ending';
        this.endingScroll = 0;
        GameAudio.playMusic('ending');
    },

    // Main game loop
    run() {
        let lastTime = performance.now();
        const loop = (now) => {
            const dt = Math.min((now - lastTime) / 1000, 0.05); // Cap at 50ms
            lastTime = now;

            this.update(dt);
            this.render();
            this.justPressed = {};

            requestAnimationFrame(loop);
        };
        requestAnimationFrame(loop);
    },

    update(dt) {
        switch (this.state) {
            case 'loading':
                break;

            case 'title':
                this.titleBlink += dt;
                if (this.justPressed['Space']) {
                    this.startGame();
                }
                break;

            case 'playing':
                this.updatePlaying(dt);
                Maps.updateFade(dt);
                Inventory.updateNotif(dt);
                break;

            case 'dialog':
                Dialog.update(dt);
                if (this.justPressed['Space'] || this.justPressed['Enter'] || this.justPressed['KeyE']) {
                    Dialog.advance();
                    if (!Dialog.active && this.state === 'dialog') {
                        this.state = 'playing';
                    }
                }
                break;

            case 'inventory':
                if (this.justPressed['KeyI'] || this.justPressed['Escape']) {
                    Inventory.visible = false;
                    this.state = 'playing';
                }
                break;

            case 'ending':
                this.endingScroll += this.endingSpeed * dt;
                if (this.justPressed['Space']) {
                    // Check if scroll is past the end
                    const totalH = ENDING_TEXT.length * 28 + this.HEIGHT;
                    if (this.endingScroll > totalH - 100) {
                        this.startTitle();
                    } else {
                        this.endingScroll += 200; // Speed up
                    }
                }
                break;
        }
    },

    updatePlaying(dt) {
        Entities.update(dt);

        // Movement input
        if (!Maps.fading) {
            let dx = 0, dy = 0;
            if (this.keys['ArrowUp']    || this.keys['KeyW']) dy = -1;
            if (this.keys['ArrowDown']  || this.keys['KeyS']) dy = 1;
            if (this.keys['ArrowLeft']  || this.keys['KeyA']) dx = -1;
            if (this.keys['ArrowRight'] || this.keys['KeyD']) dx = 1;

            // No diagonal — prioritize vertical
            if (dx !== 0 && dy !== 0) dx = 0;

            if (dx !== 0 || dy !== 0) {
                Entities.tryMove(dx, dy);
            }

            // Check if dialog was triggered by movement (e.g. walking on item)
            if (Dialog.active) {
                this.state = 'dialog';
                return;
            }

            // Interact
            if (this.justPressed['Space'] || this.justPressed['KeyE']) {
                if (Entities.interact()) {
                    if (Dialog.active) {
                        this.state = 'dialog';
                    }
                }
            }

            // Inventory
            if (this.justPressed['KeyI']) {
                Inventory.visible = true;
                this.state = 'inventory';
            }
        }

        // Update camera
        this.updateCamera();
    },

    updateCamera() {
        if (!Maps.current) return;
        const rs = Maps.RENDER_SIZE;
        const targetX = Entities.player.x * rs + rs/2 - this.WIDTH/2;
        const targetY = Entities.player.y * rs + rs/2 - this.HEIGHT/2;
        const maxX = Maps.current.width * rs - this.WIDTH;
        const maxY = Maps.current.height * rs - this.HEIGHT;
        this.camX = Math.max(0, Math.min(maxX, targetX));
        this.camY = Math.max(0, Math.min(maxY, targetY));
    },

    render() {
        const ctx = this.ctx;
        ctx.clearRect(0, 0, this.WIDTH, this.HEIGHT);

        switch (this.state) {
            case 'loading':
                this.renderLoading(ctx);
                break;
            case 'title':
                this.renderTitle(ctx);
                break;
            case 'playing':
            case 'dialog':
            case 'inventory':
                this.renderGame(ctx);
                break;
            case 'ending':
                this.renderEnding(ctx);
                break;
        }
    },

    renderLoading(ctx) {
        ctx.fillStyle = '#000';
        ctx.fillRect(0, 0, this.WIDTH, this.HEIGHT);
        ctx.fillStyle = '#fff';
        ctx.font = '16px monospace';
        ctx.textAlign = 'center';
        ctx.fillText('Loading...', this.WIDTH/2, this.HEIGHT/2);
        ctx.textAlign = 'left';
    },

    renderTitle(ctx) {
        ctx.fillStyle = '#1a1a2e';
        ctx.fillRect(0, 0, this.WIDTH, this.HEIGHT);

        // Decorative border
        ctx.strokeStyle = '#ffcc00';
        ctx.lineWidth = 3;
        ctx.strokeRect(20, 20, this.WIDTH - 40, this.HEIGHT - 40);

        // Title
        ctx.fillStyle = '#ffcc00';
        ctx.font = 'bold 48px monospace';
        ctx.textAlign = 'center';
        ctx.fillText('MVPQuest', this.WIDTH/2, 140);

        // Subtitle
        ctx.fillStyle = '#e74c3c';
        ctx.font = '18px monospace';
        ctx.fillText('Ship the MVP. Save the Company.', this.WIDTH/2, 180);
        ctx.fillText('(Destroy Production.)', this.WIDTH/2, 205);

        // Tagline
        ctx.fillStyle = '#888';
        ctx.font = '14px monospace';
        ctx.fillText('"Where every sprint is a marathon and every bug is a feature"', this.WIDTH/2, 260);

        // Controls
        ctx.fillStyle = '#aaa';
        ctx.font = '13px monospace';
        ctx.fillText('WASD / Arrows: Move    SPACE/E: Interact    I: Inventory', this.WIDTH/2, 320);

        // Blinking "Press SPACE"
        if (Math.floor(this.titleBlink * 2) % 2 === 0) {
            ctx.fillStyle = '#fff';
            ctx.font = 'bold 20px monospace';
            ctx.fillText('PRESS SPACE TO START', this.WIDTH/2, 400);
        }

        // Credits
        ctx.fillStyle = '#555';
        ctx.font = '11px monospace';
        ctx.fillText('Art: Kenney.nl  |  Made on a train to NYC', this.WIDTH/2, 450);

        ctx.textAlign = 'left';
    },

    renderGame(ctx) {
        // Map
        Maps.render(ctx, this.camX, this.camY, this.WIDTH, this.HEIGHT);

        // Entities
        Entities.render(ctx, this.camX, this.camY);

        // UI overlays
        Quests.renderHUD(ctx, this.WIDTH);
        Inventory.renderNotif(ctx, this.WIDTH);

        // Map name indicator (brief)
        if (Maps.current) {
            ctx.fillStyle = 'rgba(0,0,0,0.5)';
            ctx.fillRect(0, this.HEIGHT - 22, this.WIDTH, 22);
            ctx.fillStyle = '#aaa';
            ctx.font = '11px monospace';
            ctx.fillText('  ' + Maps.current.name + '  |  WASD: Move  SPACE: Talk  I: Items', 4, this.HEIGHT - 7);
        }

        // Dialog overlay
        if (this.state === 'dialog') {
            Dialog.render(ctx, this.WIDTH, this.HEIGHT);
        }

        // Inventory overlay
        if (this.state === 'inventory') {
            Inventory.render(ctx, this.WIDTH, this.HEIGHT);
        }

        // Fade effect
        Maps.renderFade(ctx, this.WIDTH, this.HEIGHT);
    },

    renderEnding(ctx) {
        ctx.fillStyle = '#000';
        ctx.fillRect(0, 0, this.WIDTH, this.HEIGHT);

        ctx.fillStyle = '#fff';
        ctx.font = '18px monospace';
        ctx.textAlign = 'center';

        for (let i = 0; i < ENDING_TEXT.length; i++) {
            const y = this.HEIGHT + i * 28 - this.endingScroll;
            if (y > -30 && y < this.HEIGHT + 30) {
                const line = ENDING_TEXT[i];
                // Title lines in gold
                if (line.includes('M V P') || line.includes('SHIPPED')) {
                    ctx.fillStyle = '#ffcc00';
                    ctx.font = 'bold 22px monospace';
                } else if (line.includes('PRESS SPACE')) {
                    ctx.fillStyle = Math.floor(performance.now()/500) % 2 ? '#fff' : '#555';
                    ctx.font = 'bold 16px monospace';
                } else {
                    ctx.fillStyle = '#ccc';
                    ctx.font = '16px monospace';
                }
                ctx.fillText(line, this.WIDTH/2, y);
            }
        }
        ctx.textAlign = 'left';
    },
};

// ── Bootstrap ────────────────────────────────────────────────
window.addEventListener('DOMContentLoaded', () => {
    Engine.init();
    Engine.run();
});
