/* Main boot sequence and shell controller */

const Main = {
    init() {
        LoginPanel.render();
    },

    async enterGameShell() {
        // Hide login, show game shell
        hide(document.getElementById('login-screen'));
        show(document.getElementById('game-shell'));

        // Load zone data
        const zone = await API.getZone(GameState.zoneId);
        GameState.zone = zone;
        GameState.buildTileMap(zone);

        // Load nearby entities
        await this.refreshEntities();

        // Load resources for HUD
        const resources = await API.getCharacterResources(GameState.characterId);
        GameState.character.resources = resources;

        // Init map
        MapRenderer.init(document.getElementById('map-canvas'));
        MapRenderer.render();

        // Init HUD
        HUD.render();

        // Init input
        Input.init();

        // Nav bar
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const panel = btn.dataset.panel;
                if (panel === 'menu') {
                    this._showMenu();
                } else {
                    this.togglePanel(panel);
                }
            });
        });
    },

    async refreshEntities() {
        try {
            const entities = await API.getNearbyEntities(GameState.zoneId, GameState.x, GameState.y, 20);
            GameState.entities = entities;
        } catch (e) {
            // Keep existing entities on failure
        }
    },

    // Panel management
    togglePanel(name) {
        if (GameState.activePanel === name) {
            this.closePanel();
            return;
        }
        this.openPanel(name);
    },

    async openPanel(name) {
        const container = document.getElementById('panel-container');
        const overlay = document.getElementById('panel-overlay');

        // Update active nav button
        document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
        const activeBtn = document.querySelector(`.nav-btn[data-panel="${name}"]`);
        if (activeBtn) activeBtn.classList.add('active');

        GameState.activePanel = name;
        show(overlay);
        show(container);

        // Render panel content
        const panels = {
            profile: ProfilePanel,
            inventory: InventoryPanel,
            equipment: EquipmentPanel,
            skills: SkillsPanel,
        };
        const panel = panels[name];
        if (panel) await panel.render(container);

        // Animate in
        requestAnimationFrame(() => container.classList.add('open'));

        // Close on overlay click
        overlay.onclick = () => this.closePanel();
    },

    closePanel() {
        const container = document.getElementById('panel-container');
        const overlay = document.getElementById('panel-overlay');
        container.classList.remove('open');
        document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
        GameState.activePanel = null;

        setTimeout(() => {
            hide(overlay);
            hide(container);
        }, 250);
    },

    // Entity popup
    async showEntityPopup(entity) {
        const popup = document.getElementById('entity-popup');
        clearChildren(popup);

        let detail;
        try {
            detail = await API.getEntity(entity.entity_id);
        } catch (e) {
            detail = entity;
        }

        const name = (detail.state_blob && detail.state_blob.name) || detail.entity_type;
        popup.appendChild(el('h3', null, name));
        popup.appendChild(el('p', null, `Type: ${detail.entity_type}`));
        popup.appendChild(el('p', null, `Position: (${detail.x}, ${detail.y})`));

        if (detail.state_blob && detail.state_blob.dialogue) {
            popup.appendChild(el('p', { style: 'color:#f0c040;font-style:italic;margin-top:8px;' },
                `"${detail.state_blob.dialogue}"`));
        }

        const actions = el('div', { className: 'popup-actions' });

        if (detail.entity_type === 'container') {
            actions.appendChild(el('button', {
                className: 'btn btn-primary', textContent: 'Loot',
                onClick: () => this._lootContainer(detail),
            }));
        }

        if (detail.entity_type === 'item') {
            actions.appendChild(el('button', {
                className: 'btn btn-primary', textContent: 'Pick Up',
                onClick: () => this._pickupItem(detail),
            }));
        }

        actions.appendChild(el('button', {
            className: 'btn btn-secondary', textContent: 'Close',
            onClick: () => hide(popup),
        }));

        popup.appendChild(actions);
        show(popup);
    },

    async _lootContainer(entity) {
        const popup = document.getElementById('entity-popup');
        if (!entity.state_blob || !entity.state_blob.loot) {
            showToast('Nothing to loot');
            hide(popup);
            return;
        }

        try {
            for (const lootItem of entity.state_blob.loot) {
                const result = await API.addItemToInventory(GameState.characterId, lootItem.item_def_id, lootItem.quantity);
                showToast(`Picked up ${result.item_name}${result.quantity > 1 ? ' x' + result.quantity : ''}`);
            }
            hide(popup);
            await this.refreshEntities();
            MapRenderer.render();
        } catch (e) {
            showToast('Loot failed: ' + e.message);
        }
    },

    async _pickupItem(entity) {
        const popup = document.getElementById('entity-popup');
        try {
            const result = await API.pickupItem(GameState.characterId, entity.entity_id);
            showToast(`Picked up ${result.item_name}${result.quantity > 1 ? ' x' + result.quantity : ''}`);
            hide(popup);
            await this.refreshEntities();
            MapRenderer.render();
        } catch (e) {
            showToast('Pickup failed: ' + e.message);
        }
    },

    _showMenu() {
        const popup = document.getElementById('entity-popup');
        clearChildren(popup);
        popup.appendChild(el('h3', null, 'Menu'));
        const actions = el('div', { className: 'popup-actions', style: 'flex-direction:column;' });
        actions.appendChild(el('button', {
            className: 'btn btn-secondary', textContent: 'Leave World',
            onClick: () => this._leaveWorld(),
        }));
        actions.appendChild(el('button', {
            className: 'btn btn-secondary', textContent: 'Close',
            onClick: () => hide(popup),
        }));
        popup.appendChild(actions);
        show(popup);
    },

    async _leaveWorld() {
        try {
            await API.leaveWorld(GameState.characterId);
            hide(document.getElementById('entity-popup'));
            hide(document.getElementById('game-shell'));
            show(document.getElementById('login-screen'));
            // Keep session, go back to character select
            LoginPanel._showCharacterSelect();
        } catch (e) {
            showToast('Failed to leave: ' + e.message);
        }
    },
};

// Boot
document.addEventListener('DOMContentLoaded', () => Main.init());
