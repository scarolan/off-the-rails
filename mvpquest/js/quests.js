// ── Quest System ──────────────────────────────────────────────
// Tracks quest progress, flags, and HUD display

const Quests = {
    flags: {},
    currentStep: 0, // index into QUEST_CHAIN
    questStarted: false,

    set(flag, value) {
        this.flags[flag] = value;
    },

    get(flag) {
        return this.flags[flag] || false;
    },

    // Called by dialog onEnd actions
    triggerAction(action) {
        switch (action) {
            case 'start_quest':
                this.questStarted = true;
                this.currentStep = 1; // Move past "welcome"
                GameAudio.play('quest');
                break;
            case 'give_duck':
                Inventory.add('rubber_duck');
                Inventory.showPickup('rubber_duck');
                this.set('has_duck', true);
                break;
            case 'give_ticket':
                Inventory.add('jira_ticket');
                Inventory.showPickup('jira_ticket');
                this.set('has_ticket', true);
                break;
            case 'give_yaml':
                Inventory.add('yaml_scroll');
                Inventory.showPickup('yaml_scroll');
                this.set('has_yaml', true);
                this.advanceQuestIfNeeded();
                break;
            case 'give_apikey':
                Inventory.add('api_key');
                Inventory.showPickup('api_key');
                this.set('has_apikey', true);
                this.advanceQuestIfNeeded();
                break;
            case 'give_env':
                Inventory.add('env_file');
                Inventory.showPickup('env_file');
                this.set('has_env', true);
                this.set('boss_defeated', true);
                this.advanceQuestIfNeeded();
                break;
            case 'finish_game':
                Engine.startEnding();
                break;
        }
    },

    advanceQuestIfNeeded() {
        // Check if all three artifacts collected
        if (this.get('has_yaml') && this.get('has_apikey') && this.get('has_env')) {
            this.currentStep = 4; // ship_it
        } else if (this.get('has_yaml') && this.currentStep < 2) {
            this.currentStep = 2;
        } else if (this.get('has_apikey') && this.currentStep < 3) {
            this.currentStep = 3;
        }
        GameAudio.play('quest');
    },

    // Get the dialog ID for an NPC based on quest state
    getDialog(npcId) {
        switch (npcId) {
            case 'merlin':
                return this.questStarted ? 'merlin_later' : 'merlin_intro';
            case 'datadave':
                return this.get('has_duck') ? 'datadave_later' : 'datadave_intro';
            case 'karen':
                if (!this.questStarted) return 'karen_intro';
                if (this.get('has_yaml') && this.get('has_apikey') && this.get('has_env'))
                    return 'karen_complete';
                return 'karen_progress';
            case 'priya':
                return this.get('has_ticket') ? 'priya_later' : 'priya_intro';
            case 'oracle':
                return 'oracle_talk';
            case 'steve':
                return this.get('has_ticket') ? 'steve_hasticket' : 'steve_noticket';
            case 'boss':
                return this.get('boss_defeated') ? 'boss_defeated' : 'boss_intro';
        }
        return null;
    },

    renderHUD(ctx, canvasW) {
        if (!this.questStarted) return;
        const quest = QUEST_CHAIN[this.currentStep];
        if (!quest) return;

        // Quest tracker in top-right
        ctx.fillStyle = 'rgba(0, 0, 0, 0.6)';
        ctx.fillRect(canvasW - 280, 5, 275, 42);
        ctx.strokeStyle = '#ffcc00';
        ctx.lineWidth = 1;
        ctx.strokeRect(canvasW - 280, 5, 275, 42);

        ctx.fillStyle = '#ffcc00';
        ctx.font = 'bold 11px monospace';
        ctx.fillText('QUEST: ' + quest.label, canvasW - 272, 20);

        ctx.fillStyle = '#ccc';
        ctx.font = '11px monospace';
        ctx.fillText(quest.desc, canvasW - 272, 38);

        // Artifact tracker icons
        const artifacts = [
            { key: 'has_yaml', label: 'YAML' },
            { key: 'has_apikey', label: 'KEY' },
            { key: 'has_env', label: '.env' },
        ];
        const startX = 10;
        ctx.fillStyle = 'rgba(0,0,0,0.6)';
        ctx.fillRect(startX, 5, 200, 22);
        for (let i = 0; i < artifacts.length; i++) {
            const has = this.get(artifacts[i].key);
            ctx.fillStyle = has ? '#0f0' : '#555';
            ctx.font = '11px monospace';
            ctx.fillText((has ? '✓ ' : '○ ') + artifacts[i].label, startX + 5 + i * 65, 20);
        }
    },
};
