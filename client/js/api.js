/* API fetch wrapper for all server endpoints */

const API = {
    _base: '',

    async _fetch(method, path, body) {
        const opts = { method, headers: {} };
        if (body !== undefined) {
            opts.headers['Content-Type'] = 'application/json';
            opts.body = JSON.stringify(body);
        }
        const res = await fetch(this._base + path, opts);
        if (!res.ok) {
            const err = await res.json().catch(() => ({ detail: res.statusText }));
            throw new Error(err.detail || res.statusText);
        }
        return res.json();
    },

    // Auth
    authenticate(username, password) {
        return this._fetch('POST', '/auth/login', { username, password });
    },

    // Characters
    listCharacters(accountId) {
        return this._fetch('GET', `/characters/?account_id=${encodeURIComponent(accountId)}`);
    },
    createCharacter(accountId, name, archetype) {
        return this._fetch('POST', '/characters/', { account_id: accountId, character_name: name, archetype });
    },
    loadCharacter(characterId) {
        return this._fetch('GET', `/characters/${characterId}`);
    },
    enterWorld(characterId) {
        return this._fetch('POST', `/characters/${characterId}/enter`);
    },
    leaveWorld(characterId) {
        return this._fetch('POST', `/characters/${characterId}/leave`);
    },

    // World
    getZone(zoneId) {
        return this._fetch('GET', `/world/zones/${zoneId}`);
    },
    attemptMove(characterId, direction) {
        return this._fetch('POST', `/world/characters/${characterId}/move`, { direction });
    },
    getNearbyEntities(zoneId, x, y, radius = 10) {
        return this._fetch('GET', `/world/zones/${zoneId}/entities?x=${x}&y=${y}&radius=${radius}`);
    },
    getEntity(entityId) {
        return this._fetch('GET', `/world/entities/${entityId}`);
    },

    // Inventory & Equipment
    getInventory(characterId) {
        return this._fetch('GET', `/characters/${characterId}/inventory`);
    },
    addItemToInventory(characterId, itemDefId, quantity = 1) {
        return this._fetch('POST', `/characters/${characterId}/inventory`, { item_def_id: itemDefId, quantity });
    },
    dropItem(characterId, itemInstanceId, quantity = null) {
        return this._fetch('POST', `/characters/${characterId}/inventory/${itemInstanceId}/drop`, { quantity });
    },
    pickupItem(characterId, entityId) {
        return this._fetch('POST', `/characters/${characterId}/pickup/${entityId}`);
    },
    equipItem(characterId, itemInstanceId, slotId) {
        return this._fetch('POST', `/characters/${characterId}/equip`, { item_instance_id: itemInstanceId, slot_id: slotId });
    },
    unequipItem(characterId, slotId) {
        return this._fetch('DELETE', `/characters/${characterId}/equip/${slotId}`);
    },
    getEquipment(characterId) {
        return this._fetch('GET', `/characters/${characterId}/equipment`);
    },

    // Character State
    getCharacterProfile(characterId) {
        return this._fetch('GET', `/characters/${characterId}/profile`);
    },
    getCharacterAttributes(characterId) {
        return this._fetch('GET', `/characters/${characterId}/attributes`);
    },
    getCharacterResources(characterId) {
        return this._fetch('GET', `/characters/${characterId}/resources`);
    },
    getCharacterSkills(characterId) {
        return this._fetch('GET', `/characters/${characterId}/skills`);
    },
};
