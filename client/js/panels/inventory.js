/* Inventory panel */

const InventoryPanel = {
    async render(container) {
        clearChildren(container);
        container.appendChild(el('div', { className: 'panel-header' },
            el('h2', null, 'Inventory'),
            el('button', { className: 'panel-close', textContent: '\u00D7', onClick: () => Main.closePanel() }),
        ));

        const body = el('div', { className: 'panel-body' });
        container.appendChild(body);

        try {
            const items = await API.getInventory(GameState.characterId);
            if (items.length === 0) {
                body.appendChild(el('p', { className: 'empty-state', textContent: 'Inventory is empty' }));
                return;
            }
            for (const item of items) {
                const row = el('div', { className: 'item-row' },
                    el('div', { className: 'item-info' },
                        el('div', { className: 'item-name', textContent: item.item_name }),
                        el('div', { className: 'item-detail', textContent: `${item.item_category}${item.quantity > 1 ? ' x' + item.quantity : ''}` }),
                    ),
                );

                const actions = el('div', { className: 'item-actions' });
                if (item.item_category === 'weapon' || item.item_category === 'armor') {
                    actions.appendChild(el('button', {
                        className: 'btn btn-primary', textContent: 'Equip',
                        onClick: () => this._equip(item),
                    }));
                }
                actions.appendChild(el('button', {
                    className: 'btn btn-secondary', textContent: 'Drop',
                    onClick: () => this._drop(item),
                }));
                row.appendChild(actions);
                body.appendChild(row);
            }
        } catch (e) {
            body.appendChild(el('p', { className: 'empty-state', textContent: 'Failed to load inventory' }));
        }
    },

    async _equip(item) {
        try {
            // Determine slot from category
            const slotMap = { weapon: 'main_hand', armor: 'chest' };
            const slot = slotMap[item.item_category] || 'main_hand';
            await API.equipItem(GameState.characterId, item.item_instance_id, slot);
            showToast(`Equipped ${item.item_name}`);
            await this.render(document.getElementById('panel-container'));
            HUD.refresh();
        } catch (e) {
            showToast('Equip failed: ' + e.message);
        }
    },

    async _drop(item) {
        try {
            await API.dropItem(GameState.characterId, item.item_instance_id);
            showToast(`Dropped ${item.item_name}`);
            await this.render(document.getElementById('panel-container'));
            await Main.refreshEntities();
            MapRenderer.render();
        } catch (e) {
            showToast('Drop failed: ' + e.message);
        }
    },
};
