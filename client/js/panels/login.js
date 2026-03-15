/* Login & Character Select panel */

const LoginPanel = {
    render() {
        const screen = document.getElementById('login-screen');
        clearChildren(screen);
        screen.appendChild(this._loginForm());
    },

    _loginForm() {
        const box = el('div', { className: 'login-box' },
            el('h1', null, 'Baby RPG'),
            el('div', { className: 'form-group' },
                el('label', null, 'Username'),
                el('input', { type: 'text', id: 'login-user', placeholder: 'Enter username' }),
            ),
            el('div', { className: 'form-group' },
                el('label', null, 'Password'),
                el('input', { type: 'password', id: 'login-pass', placeholder: 'Enter password' }),
            ),
            el('button', { className: 'btn btn-primary', id: 'login-btn', textContent: 'Login', onClick: () => this._onLogin() }),
        );
        return box;
    },

    async _onLogin() {
        const username = document.getElementById('login-user').value.trim();
        const password = document.getElementById('login-pass').value;
        if (!username) return showToast('Enter a username');

        try {
            const res = await API.authenticate(username, password);
            GameState.sessionToken = res.session_token;
            GameState.accountId = res.account_id;
            await this._showCharacterSelect();
        } catch (e) {
            showToast('Login failed: ' + e.message);
        }
    },

    async _showCharacterSelect() {
        const screen = document.getElementById('login-screen');
        clearChildren(screen);

        const chars = await API.listCharacters(GameState.accountId);

        const box = el('div', { className: 'login-box' },
            el('h1', null, 'Baby RPG'),
            el('h2', null, 'Your Characters'),
        );

        if (chars.length > 0) {
            const list = el('div', { className: 'char-list' });
            for (const c of chars) {
                const card = el('div', { className: 'char-card', onClick: () => this._selectCharacter(c.character_id) },
                    el('div', { className: 'char-card-info' },
                        el('div', { className: 'name', textContent: c.character_name }),
                        el('div', { className: 'detail', textContent: `Level ${c.level} ${c.archetype || ''}` }),
                    ),
                    el('span', { textContent: '\u25B6', style: 'color: #f0c040; font-size: 18px;' }),
                );
                list.appendChild(card);
            }
            box.appendChild(list);
        } else {
            box.appendChild(el('p', { className: 'empty-state', textContent: 'No characters yet' }));
        }

        box.appendChild(el('h2', null, 'Create New Character'));
        box.appendChild(el('div', { className: 'form-group' },
            el('label', null, 'Name'),
            el('input', { type: 'text', id: 'create-name', placeholder: 'Character name' }),
        ));
        box.appendChild(el('div', { className: 'form-group' },
            el('label', null, 'Archetype'),
            (() => {
                const sel = el('select', { id: 'create-archetype' });
                for (const a of ['warrior', 'mage', 'rogue']) {
                    sel.appendChild(el('option', { value: a, textContent: a.charAt(0).toUpperCase() + a.slice(1) }));
                }
                return sel;
            })(),
        ));
        box.appendChild(el('button', {
            className: 'btn btn-secondary', textContent: 'Create & Enter',
            onClick: () => this._createCharacter(),
        }));

        screen.appendChild(box);
    },

    async _selectCharacter(characterId) {
        try {
            const entry = await API.enterWorld(characterId);
            GameState.characterId = characterId;
            GameState.entityId = entry.entity_id;
            GameState.zoneId = entry.zone_id;
            const charDetail = await API.loadCharacter(characterId);
            GameState.character = charDetail;
            GameState.character.x = entry.x;
            GameState.character.y = entry.y;
            GameState.entities = entry.nearby_entities;
            Main.enterGameShell();
        } catch (e) {
            showToast('Failed to enter world: ' + e.message);
        }
    },

    async _createCharacter() {
        const name = document.getElementById('create-name').value.trim();
        const archetype = document.getElementById('create-archetype').value;
        if (!name) return showToast('Enter a character name');

        try {
            const char = await API.createCharacter(GameState.accountId, name, archetype);
            await this._selectCharacter(char.character_id);
        } catch (e) {
            showToast('Failed to create character: ' + e.message);
        }
    },
};
