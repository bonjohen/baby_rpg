/* Skills panel */

const SkillsPanel = {
    async render(container) {
        clearChildren(container);
        container.appendChild(el('div', { className: 'panel-header' },
            el('h2', null, 'Skills'),
            el('button', { className: 'panel-close', textContent: '\u00D7', onClick: () => Main.closePanel() }),
        ));

        const body = el('div', { className: 'panel-body' });
        container.appendChild(body);

        try {
            const data = await API.getCharacterSkills(GameState.characterId);
            if (!data.skills || data.skills.length === 0) {
                body.appendChild(el('p', { className: 'empty-state', textContent: 'No skills learned yet' }));
                return;
            }
            for (const skill of data.skills) {
                body.appendChild(el('div', { className: 'stat-row' },
                    el('span', { className: 'label', textContent: skill.name }),
                    el('span', { className: 'value', textContent: `Rank ${skill.rank}` }),
                ));
            }
        } catch (e) {
            body.appendChild(el('p', { className: 'empty-state', textContent: 'Failed to load skills' }));
        }
    },
};
