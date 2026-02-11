// ── Audio System ──────────────────────────────────────────────
// Loads and plays OGG sound effects and music loops

const GameAudio = {
    sounds: {},
    music: null,
    musicElement: null,
    enabled: true,
    musicVolume: 0.3,
    sfxVolume: 0.5,

    SOUND_DEFS: {
        footstep:  'assets/Audio/RPG Audio/Audio/footstep00.ogg',
        footstep2: 'assets/Audio/RPG Audio/Audio/footstep01.ogg',
        door:      'assets/Audio/RPG Audio/Audio/doorOpen_1.ogg',
        item:      'assets/Audio/RPG Audio/Audio/handleCoins.ogg',
        talk:      'assets/Audio/RPG Audio/Audio/bookFlip1.ogg',
        quest:     'assets/Audio/RPG Audio/Audio/metalClick.ogg',
        error:     'assets/Audio/RPG Audio/Audio/doorClose_4.ogg',
    },

    MUSIC_DEFS: {
        town:    'assets/Audio/Music Loops/Loops/Farm Frolics.ogg',
        office:  'assets/Audio/Music Loops/Loops/Wacky Waiting.ogg',
        dungeon: 'assets/Audio/Music Loops/Retro/Retro Mystic.ogg',
        boss:    'assets/Audio/Music Loops/Loops/Infinite Descent.ogg',
        title:   'assets/Audio/Music Loops/Retro/Retro Comedy.ogg',
        ending:  'assets/Audio/Music Loops/Loops/Sad Town.ogg',
    },

    load(callback) {
        // Pre-create audio pools for SFX
        for (const [name, path] of Object.entries(this.SOUND_DEFS)) {
            this.sounds[name] = [];
            for (let i = 0; i < 3; i++) {
                const audio = new Audio(path);
                audio.volume = this.sfxVolume;
                audio.preload = 'auto';
                this.sounds[name].push(audio);
            }
        }
        // Don't block on loading — audio loads lazily
        callback();
    },

    play(name) {
        if (!this.enabled) return;
        const pool = this.sounds[name];
        if (!pool) return;
        // Find an available audio element from the pool
        for (const audio of pool) {
            if (audio.paused || audio.ended) {
                audio.currentTime = 0;
                audio.volume = this.sfxVolume;
                audio.play().catch(() => {});
                return;
            }
        }
        // All busy — reset first one
        pool[0].currentTime = 0;
        pool[0].play().catch(() => {});
    },

    playFootstep() {
        this.play(Math.random() < 0.5 ? 'footstep' : 'footstep2');
    },

    playMusic(name) {
        if (!this.enabled) return;
        const path = this.MUSIC_DEFS[name];
        if (!path) return;
        if (this.music === name && this.musicElement && !this.musicElement.paused) return;
        this.stopMusic();
        this.music = name;
        this.musicElement = new Audio(path);
        this.musicElement.loop = true;
        this.musicElement.volume = this.musicVolume;
        this.musicElement.play().catch(() => {});
    },

    stopMusic() {
        if (this.musicElement) {
            this.musicElement.pause();
            this.musicElement.currentTime = 0;
            this.musicElement = null;
        }
        this.music = null;
    },
};
