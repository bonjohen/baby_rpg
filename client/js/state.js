/* Client-side state store */

const GameState = {
    // Session
    sessionToken: null,
    accountId: null,

    // Character
    characterId: null,
    entityId: null,
    character: null,  // full detail from loadCharacter

    // Zone
    zoneId: null,
    zone: null,       // zone detail with tiles
    tileMap: null,    // 2D array [y][x] for fast lookup

    // Entities
    entities: [],

    // UI
    activePanel: null,

    // Position helpers
    get x() { return this.character ? this.character.x : 0; },
    get y() { return this.character ? this.character.y : 0; },

    setPosition(x, y) {
        if (this.character) {
            this.character.x = x;
            this.character.y = y;
        }
    },

    buildTileMap(zone) {
        const map = [];
        for (let y = 0; y < zone.height; y++) {
            map[y] = new Array(zone.width).fill(null);
        }
        for (const tile of zone.tiles) {
            map[tile.y][tile.x] = tile;
        }
        this.tileMap = map;
    },

    reset() {
        this.sessionToken = null;
        this.accountId = null;
        this.characterId = null;
        this.entityId = null;
        this.character = null;
        this.zoneId = null;
        this.zone = null;
        this.tileMap = null;
        this.entities = [];
        this.activePanel = null;
    },
};
