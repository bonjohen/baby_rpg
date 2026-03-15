/* Canvas tile map renderer */

const TERRAIN_COLORS = {
    grass: '#4a7c40',
    wall: '#6b6b6b',
    water: '#3a6ea5',
    tree: '#2d5a1e',
    stone: '#a08060',
};

const ENTITY_STYLES = {
    player: { color: '#f0c040', shape: 'circle' },
    npc: { color: '#40a0f0', shape: 'circle' },
    container: { color: '#c07020', shape: 'square' },
    item: { color: '#e04080', shape: 'diamond' },
};

const MIN_TILE_SIZE = 32;

const MapRenderer = {
    canvas: null,
    ctx: null,
    tileSize: 0,
    offsetX: 0,
    offsetY: 0,

    init(canvas) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this._resize();
        window.addEventListener('resize', () => { this._resize(); this.render(); });

        // Click handler for entity interaction
        canvas.addEventListener('click', (e) => this._onClick(e));
    },

    _resize() {
        const parent = this.canvas.parentElement;
        this.canvas.width = parent.clientWidth;
        this.canvas.height = parent.clientHeight;
    },

    render() {
        if (!GameState.zone || !GameState.tileMap) return;
        const ctx = this.ctx;
        const zone = GameState.zone;
        const W = this.canvas.width;
        const H = this.canvas.height;

        // Calculate tile size
        const fitW = Math.floor(W / zone.width);
        const fitH = Math.floor(H / zone.height);
        this.tileSize = Math.max(MIN_TILE_SIZE, Math.min(fitW, fitH));

        const mapW = zone.width * this.tileSize;
        const mapH = zone.height * this.tileSize;

        // Viewport offset to center on player
        if (mapW <= W) {
            this.offsetX = Math.floor((W - mapW) / 2);
        } else {
            const playerPixelX = GameState.x * this.tileSize + this.tileSize / 2;
            this.offsetX = Math.floor(W / 2 - playerPixelX);
            this.offsetX = Math.min(0, Math.max(W - mapW, this.offsetX));
        }
        if (mapH <= H) {
            this.offsetY = Math.floor((H - mapH) / 2);
        } else {
            const playerPixelY = GameState.y * this.tileSize + this.tileSize / 2;
            this.offsetY = Math.floor(H / 2 - playerPixelY);
            this.offsetY = Math.min(0, Math.max(H - mapH, this.offsetY));
        }

        // Clear
        ctx.fillStyle = '#111';
        ctx.fillRect(0, 0, W, H);

        // Draw terrain
        for (let y = 0; y < zone.height; y++) {
            for (let x = 0; x < zone.width; x++) {
                const tile = GameState.tileMap[y][x];
                const px = this.offsetX + x * this.tileSize;
                const py = this.offsetY + y * this.tileSize;

                // Skip tiles outside viewport
                if (px + this.tileSize < 0 || px > W || py + this.tileSize < 0 || py > H) continue;

                ctx.fillStyle = TERRAIN_COLORS[tile.terrain_type] || '#333';
                ctx.fillRect(px, py, this.tileSize, this.tileSize);

                // Grid lines
                ctx.strokeStyle = 'rgba(0,0,0,0.2)';
                ctx.strokeRect(px, py, this.tileSize, this.tileSize);
            }
        }

        // Draw entities (non-player first, then player on top)
        const sorted = [...GameState.entities].sort((a, b) => {
            if (a.entity_type === 'player') return 1;
            if (b.entity_type === 'player') return -1;
            return 0;
        });

        for (const ent of sorted) {
            // Skip the current player entity from the entities list — we draw it separately
            if (ent.entity_id === GameState.entityId) continue;
            this._drawEntity(ctx, ent.x, ent.y, ent.entity_type);
        }

        // Draw player
        this._drawEntity(ctx, GameState.x, GameState.y, 'player');
    },

    _drawEntity(ctx, x, y, type) {
        const style = ENTITY_STYLES[type] || ENTITY_STYLES.npc;
        const px = this.offsetX + x * this.tileSize + this.tileSize / 2;
        const py = this.offsetY + y * this.tileSize + this.tileSize / 2;
        const r = this.tileSize * 0.35;

        ctx.fillStyle = style.color;
        ctx.strokeStyle = '#000';
        ctx.lineWidth = 1.5;

        if (style.shape === 'circle') {
            ctx.beginPath();
            ctx.arc(px, py, r, 0, Math.PI * 2);
            ctx.fill();
            ctx.stroke();
        } else if (style.shape === 'square') {
            ctx.fillRect(px - r, py - r, r * 2, r * 2);
            ctx.strokeRect(px - r, py - r, r * 2, r * 2);
        } else if (style.shape === 'diamond') {
            ctx.beginPath();
            ctx.moveTo(px, py - r);
            ctx.lineTo(px + r, py);
            ctx.lineTo(px, py + r);
            ctx.lineTo(px - r, py);
            ctx.closePath();
            ctx.fill();
            ctx.stroke();
        }
    },

    _onClick(e) {
        const rect = this.canvas.getBoundingClientRect();
        const clickX = e.clientX - rect.left;
        const clickY = e.clientY - rect.top;

        const tileX = Math.floor((clickX - this.offsetX) / this.tileSize);
        const tileY = Math.floor((clickY - this.offsetY) / this.tileSize);

        // Find entity at this tile (excluding own player)
        const entity = GameState.entities.find(ent =>
            ent.x === tileX && ent.y === tileY && ent.entity_id !== GameState.entityId
        );

        if (entity) {
            Main.showEntityPopup(entity);
        }
    },

    // Convert tile coords to check which entity is at a tile
    getEntityAtTile(tx, ty) {
        return GameState.entities.find(ent => ent.x === tx && ent.y === ty && ent.entity_id !== GameState.entityId);
    },
};
