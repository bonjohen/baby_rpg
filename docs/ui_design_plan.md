# UI Implementation Plan

This plan breaks the UI implementation into phases with actionable tasks. Each phase builds on the previous one and ends with a validation step. The design decisions behind this plan are documented in `docs/ui_design_document.md`.

## File Structure

```
client/
├── index.html
├── css/
│   └── style.css
└── js/
    ├── main.js
    ├── api.js
    ├── state.js
    ├── map.js
    ├── input.js
    ├── utils.js
    └── panels/
        ├── login.js
        ├── hud.js
        ├── profile.js
        ├── inventory.js
        ├── equipment.js
        └── skills.js
```

---

## Phase UI-1: Static Shell & API Layer

Set up the HTML structure, CSS layout, JavaScript module loading, API wrapper, and static file serving. No game logic.

[ ] Create `client/index.html` — viewport meta, canvas element, HUD container, panel container, bottom nav bar, script tags
[ ] Create `client/css/style.css` — mobile-first full-viewport layout, nav bar fixed at bottom, panel slide-over positioning, HUD fixed at top, toast area
[ ] Create `client/js/api.js` — async fetch wrapper with functions for every server endpoint (auth, characters, world, inventory, equipment)
[ ] Create `client/js/state.js` — state object: session, character, zone, entities, activePanel; getter/setter helpers
[ ] Create `client/js/utils.js` — DOM creation helpers, element show/hide, toast display function
[ ] Create `client/js/main.js` — empty boot function, wire DOMContentLoaded
[ ] Mount `client/` as static files in FastAPI (`app/main.py`)

### Phase UI-1 Validation

[ ] Server starts and serves `index.html` at root URL
[ ] Page loads with visible canvas, empty HUD, nav bar with placeholder buttons
[ ] Browser console shows no errors

---

## Phase UI-2: Login & Character Select

Build the pre-game flow from login through world entry.

[ ] Create `client/js/panels/login.js` — render login form (username, password, submit)
[ ] Add character select view to login.js — list of character cards (name, level, archetype) with select button, plus create character form (name, archetype dropdown, submit)
[ ] Wire login form submit to `api.authenticate()` → on success store session in state, fetch character list
[ ] Wire character select to `api.enterWorld()` → on success store character + zone data in state, hide login, show game shell
[ ] Wire create character to `api.createCharacter()` → on success auto-enter world
[ ] In `main.js`, boot sequence: show login panel → wait for world entry → initialize map

### Phase UI-2 Validation

[ ] Login with any username transitions to character select
[ ] Creating a character shows it in the list
[ ] Selecting a character hides login and shows the game shell (empty map canvas)

---

## Phase UI-3: Map Renderer

Draw the tile grid and entities on the canvas.

[ ] Create `client/js/map.js` — `initMap(canvas)`, `renderMap(state)` functions
[ ] Implement tile rendering: iterate zone tile grid, draw colored rectangles based on terrain_type using the color table from the design doc
[ ] Implement viewport camera: center on player position, handle zones larger than canvas with scroll offset, dark fill for out-of-bounds area
[ ] Implement entity rendering: draw shapes on top of tiles — gold circle for player, blue circle for NPC, brown square for container, pink diamond for item
[ ] Render grid lines between tiles for visual clarity
[ ] Call `renderMap()` after world entry with zone and entity data from state

### Phase UI-3 Validation

[ ] After login + enter world, canvas shows the Village Green terrain grid with correct colors
[ ] Player marker visible at starting position
[ ] NPCs (Elder Maren, Merchant Tova) and container (Old Chest) visible at their seeded positions
[ ] Resizing the browser window re-renders correctly

---

## Phase UI-4: Movement & Interaction

Connect input to movement intents and entity inspection.

[ ] Create `client/js/input.js` — keyboard listener for arrow keys and WASD, maps to direction strings
[ ] Add mobile d-pad to `index.html` / `style.css` — four directional buttons in bottom-left corner, translucent
[ ] Wire d-pad buttons to same movement handler as keyboard
[ ] Movement handler: call `api.attemptMove(characterId, direction)` → on accepted, update state position + re-render map → on rejected, show toast with reason
[ ] Refresh nearby entities after each successful move via `api.getNearbyEntities()`
[ ] Add click/tap handler on canvas: translate pixel coordinates to tile coordinates, find entity at that tile
[ ] Render entity inspect popup: show entity name, type, position; "Pick Up" button for items, "Loot" button for containers
[ ] Wire "Pick Up" to `api.pickupItem()` → refresh map + inventory
[ ] Wire "Loot" for containers: add looted items to inventory via `api.addItemToInventory()` for each loot entry

### Phase UI-4 Validation

[ ] Arrow keys / WASD move the player on the map, camera follows
[ ] Moving into walls shows "blocked by wall" toast
[ ] D-pad buttons produce the same movement
[ ] Clicking an NPC shows inspect popup with name and dialogue
[ ] Clicking the Old Chest shows loot popup, looting adds items to inventory

---

## Phase UI-5: HUD

Add the persistent status overlay.

[ ] Create `client/js/panels/hud.js` — `renderHud(state)` function
[ ] Render character name and level, left-aligned in HUD container
[ ] Render HP bar (green fill on dark background, numeric label)
[ ] Render MP bar (blue fill)
[ ] Render stamina bar (yellow fill)
[ ] Fetch resources from `api.getCharacterResources()` on world entry
[ ] Re-render HUD after any action that may change resources (equip, use consumable)

### Phase UI-5 Validation

[ ] HUD visible at top of screen with correct character name, level, and bar values
[ ] Bars show correct proportions (e.g. 100/100 = full bar)
[ ] HUD is translucent, map visible behind it

---

## Phase UI-6: Character Panels

Build the slide-over panels for profile, inventory, equipment, and skills.

### Profile

[ ] Create `client/js/panels/profile.js` — fetch from `api.getCharacterProfile()`, render name, level, XP, archetype, faction, biography
[ ] Wire nav bar "Profile" button to toggle profile panel

### Inventory

[ ] Create `client/js/panels/inventory.js` — fetch from `api.getInventory()`, render scrollable item list
[ ] Each item row shows: name, category, quantity, "Equip" button (if equippable), "Drop" button
[ ] Wire "Equip" to `api.equipItem()` → refresh inventory + equipment + HUD
[ ] Wire "Drop" to `api.dropItem()` → refresh inventory + map (new item entity on ground)
[ ] Wire nav bar "Inventory" button to toggle inventory panel

### Equipment

[ ] Create `client/js/panels/equipment.js` — fetch from `api.getEquipment()` + `api.getCharacterAttributes()`
[ ] Render slot list: slot name, equipped item name or "Empty", item stats, "Unequip" button
[ ] Render attribute summary section: base stats, equipment bonuses, effective totals
[ ] Wire "Unequip" to `api.unequipItem()` → refresh equipment + inventory + HUD
[ ] Wire nav bar "Equipment" button to toggle equipment panel

### Skills

[ ] Create `client/js/panels/skills.js` — fetch from `api.getCharacterSkills()`, render list or empty state message
[ ] Wire nav bar "Skills" button to toggle skills panel

### Panel Behavior

[ ] Only one panel open at a time — opening a panel closes any other
[ ] Panel open/close has CSS transition (slide from right)
[ ] Map is dimmed but visible behind open panel
[ ] Close button on each panel header

### Phase UI-6 Validation

[ ] Each nav button opens and closes its panel
[ ] Profile shows correct character data
[ ] Inventory lists items picked up from the Old Chest
[ ] Equipping an item from inventory moves it to equipment panel and updates attributes
[ ] Unequipping returns item to inventory
[ ] Dropping an item removes it from inventory and shows it on the map
[ ] Skills panel shows empty state gracefully

---

## Phase UI-7: Integration & Polish

Full flow testing and UX refinements.

[ ] Add "Leave World" option in menu — calls `api.leaveWorld()`, returns to character select screen
[ ] Toast messages for all action outcomes: move rejection, equip success/failure, pickup, drop, loot
[ ] Toasts auto-dismiss after 2 seconds, stack vertically
[ ] Disable movement input while a move request is in-flight (prevent rapid double-moves)
[ ] Error toast for network failures: "Connection lost — please refresh"
[ ] Verify mobile touch targets are at least 44px
[ ] Test full end-to-end flow: login → create character → enter world → move around → loot container → equip weapon + armor → check attributes → drop item → pick it back up → view all panels → leave world → re-enter at saved position

### Phase UI-7 Validation

[ ] All listed flow steps complete without errors
[ ] Leave + re-enter preserves character position
[ ] No console errors throughout the full flow
[ ] Layout is usable on a 375px-wide viewport (phone)
