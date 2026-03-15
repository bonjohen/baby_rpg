/* Keyboard and d-pad input handling */

const Input = {
    _moving: false,

    init() {
        // Keyboard
        document.addEventListener('keydown', (e) => this._onKey(e));

        // D-pad buttons
        document.querySelectorAll('.dpad-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const dir = btn.dataset.dir;
                if (dir) this._move(dir);
            });
            // Prevent long-press context menu on mobile
            btn.addEventListener('contextmenu', (e) => e.preventDefault());
        });
    },

    _onKey(e) {
        // Don't capture input when typing in forms
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'SELECT' || e.target.tagName === 'TEXTAREA') return;

        const keyMap = {
            ArrowUp: 'north', ArrowDown: 'south', ArrowLeft: 'west', ArrowRight: 'east',
            w: 'north', s: 'south', a: 'west', d: 'east',
            W: 'north', S: 'south', A: 'west', D: 'east',
        };
        const dir = keyMap[e.key];
        if (dir) {
            e.preventDefault();
            this._move(dir);
        }
    },

    async _move(direction) {
        if (this._moving || !GameState.characterId) return;
        this._moving = true;

        try {
            const result = await API.attemptMove(GameState.characterId, direction);
            if (result.accepted) {
                GameState.setPosition(result.x, result.y);
                await Main.refreshEntities();
                MapRenderer.render();
            } else {
                showToast(result.reason || 'Cannot move there');
            }
        } catch (e) {
            showToast('Connection lost \u2014 please refresh');
        } finally {
            this._moving = false;
        }
    },
};
