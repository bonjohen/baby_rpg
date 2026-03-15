/* Equipment panel */

const EquipmentPanel = {
    async render(container) {
        clearChildren(container);
        container.appendChild(el('div', { className: 'panel-header' },
            el('h2', null, 'Equipment'),
            el('button', { className: 'panel-close', textContent: '\u00D7', onClick: () => Main.closePanel() }),
        ));

        const body = el('div', { className: 'panel-body' });
        container.appendChild(body);

        try {
            const equipment = await API.getEquipment(GameState.characterId);
            const attrs = await API.getCharacterAttributes(GameState.characterId);

            const slots = ['head', 'chest', 'legs', 'feet', 'main_hand', 'off_hand'];

            body.appendChild(el('div', { className: 'section-title', textContent: 'Equipped Items' }));
            for (const slotId of slots) {
                const equipped = equipment.find(e => e.slot_id === slotId);
                const row = el('div', { className: 'slot-row' },
                    el('span', { className: 'slot-name', textContent: slotId.replace('_', ' ') }),
                );
                if (equipped) {
                    row.appendChild(el('span', { className: 'slot-item', textContent: equipped.item_name }));
                    row.appendChild(el('button', {
                        className: 'btn btn-secondary', textContent: 'Remove',
                        style: 'padding:4px 8px;font-size:11px;width:auto;',
                        onClick: () => this._unequip(slotId),
                    }));
                } else {
                    row.appendChild(el('span', { className: 'slot-item empty', textContent: 'Empty' }));
                }
                body.appendChild(row);
            }

            // Attributes section
            body.appendChild(el('div', { className: 'section-title', textContent: 'Attributes' }));
            for (const [attr, base] of Object.entries(attrs.base)) {
                const bonus = (attrs.equipment_bonuses && attrs.equipment_bonuses[attr]) || 0;
                const eff = attrs.effective[attr];
                const row = el('div', { className: 'stat-row' },
                    el('span', { className: 'label', textContent: attr.charAt(0).toUpperCase() + attr.slice(1) }),
                    el('span', { className: 'value' },
                        document.createTextNode(String(eff)),
                        bonus ? el('span', { className: 'bonus', textContent: ` (+${bonus})` }) : null,
                    ),
                );
                body.appendChild(row);
            }

            // Derived stats
            if (attrs.derived) {
                body.appendChild(el('div', { className: 'section-title', textContent: 'Combat Stats' }));
                for (const [stat, val] of Object.entries(attrs.derived)) {
                    if (val === 0) continue;
                    body.appendChild(el('div', { className: 'stat-row' },
                        el('span', { className: 'label', textContent: stat.charAt(0).toUpperCase() + stat.slice(1) }),
                        el('span', { className: 'value', textContent: String(val) }),
                    ));
                }
            }
        } catch (e) {
            body.appendChild(el('p', { className: 'empty-state', textContent: 'Failed to load equipment' }));
        }
    },

    async _unequip(slotId) {
        try {
            await API.unequipItem(GameState.characterId, slotId);
            showToast(`Unequipped ${slotId.replace('_', ' ')}`);
            await this.render(document.getElementById('panel-container'));
            HUD.refresh();
        } catch (e) {
            showToast('Unequip failed: ' + e.message);
        }
    },
};
