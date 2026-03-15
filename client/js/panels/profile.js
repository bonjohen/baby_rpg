/* Profile panel */

const ProfilePanel = {
    async render(container) {
        clearChildren(container);
        container.appendChild(el('div', { className: 'panel-header' },
            el('h2', null, 'Profile'),
            el('button', { className: 'panel-close', textContent: '\u00D7', onClick: () => Main.closePanel() }),
        ));

        const body = el('div', { className: 'panel-body' });
        container.appendChild(body);

        try {
            const p = await API.getCharacterProfile(GameState.characterId);
            const rows = [
                ['Name', p.character_name],
                ['Level', p.level],
                ['Experience', p.experience],
                ['Archetype', p.archetype || '—'],
                ['Faction', p.faction || '—'],
                ['Origin', p.origin || '—'],
            ];
            for (const [label, value] of rows) {
                body.appendChild(el('div', { className: 'stat-row' },
                    el('span', { className: 'label', textContent: label }),
                    el('span', { className: 'value', textContent: String(value) }),
                ));
            }
            if (p.biography) {
                body.appendChild(el('div', { className: 'section-title', textContent: 'Biography' }));
                body.appendChild(el('p', { textContent: p.biography, style: 'font-size:13px;color:#aaa;' }));
            }
        } catch (e) {
            body.appendChild(el('p', { className: 'empty-state', textContent: 'Failed to load profile' }));
        }
    },
};
