/* HUD overlay — character name, level, resource bars */

const HUD = {
    render() {
        const hud = document.getElementById('hud');
        clearChildren(hud);
        if (!GameState.character) return;

        const c = GameState.character;

        hud.appendChild(el('div', { className: 'hud-name', textContent: `${c.character_name} Lv${c.level}` }));

        const bars = el('div', { className: 'hud-bars' });
        const r = c.resources;
        bars.appendChild(this._bar('hp', r.health_current, r.health_max, 'HP'));
        bars.appendChild(this._bar('mp', r.mana_current, r.mana_max, 'MP'));
        bars.appendChild(this._bar('sta', r.stamina_current, r.stamina_max, 'STA'));
        hud.appendChild(bars);
    },

    _bar(cls, current, max, label) {
        const pct = max > 0 ? (current / max * 100) : 0;
        return el('div', { className: 'bar-wrap' },
            el('div', { className: `bar-fill ${cls}`, style: `width:${pct}%` }),
            el('div', { className: 'bar-label', textContent: `${label} ${current}/${max}` }),
        );
    },

    async refresh() {
        try {
            const res = await API.getCharacterResources(GameState.characterId);
            GameState.character.resources = res;
            this.render();
        } catch (e) {
            // Silently fail — HUD will show stale data
        }
    },
};
