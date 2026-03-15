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

[X] Create `client/index.html` — viewport meta, canvas element, HUD container, panel container, bottom nav bar, script tags
[X] Create `client/css/style.css` — mobile-first full-viewport layout, nav bar fixed at bottom, panel slide-over positioning, HUD fixed at top, toast area
[X] Create `client/js/api.js` — async fetch wrapper with functions for every server endpoint (auth, characters, world, inventory, equipment)
[X] Create `client/js/state.js` — state object: session, character, zone, entities, activePanel; getter/setter helpers
[X] Create `client/js/utils.js` — DOM creation helpers, element show/hide, toast display function
[X] Create `client/js/main.js` — boot function, wire DOMContentLoaded
[X] Mount `client/` as static files in FastAPI (`app/main.py`)

### Phase UI-1 Validation

[X] Server starts and serves `index.html` at root URL
[X] Page loads with visible canvas, empty HUD, nav bar with placeholder buttons
[X] Browser console shows no errors

---

## Phase UI-2: Login & Character Select

Build the pre-game flow from login through world entry.

[X] Create `client/js/panels/login.js` — render login form (username, password, submit)
[X] Add character select view to login.js — list of character cards (name, level, archetype) with select button, plus create character form (name, archetype dropdown, submit)
[X] Wire login form submit to `api.authenticate()` → on success store session in state, fetch character list
[X] Wire character select to `api.enterWorld()` → on success store character + zone data in state, hide login, show game shell
[X] Wire create character to `api.createCharacter()` → on success auto-enter world
[X] In `main.js`, boot sequence: show login panel → wait for world entry → initialize map

### Phase UI-2 Validation

[X] Login with any username transitions to character select
[X] Creating a character shows it in the list
[X] Selecting a character hides login and shows the game shell (empty map canvas)

---

## Phase UI-3: Map Renderer

Draw the tile grid and entities on the canvas.

[X] Create `client/js/map.js` — `initMap(canvas)`, `renderMap(state)` functions
[X] Implement tile rendering: iterate zone tile grid, draw colored rectangles based on terrain_type using the color table from the design doc
[X] Implement viewport camera: center on player position, handle zones larger than canvas with scroll offset, dark fill for out-of-bounds area
[X] Implement entity rendering: draw shapes on top of tiles — gold circle for player, blue circle for NPC, brown square for container, pink diamond for item
[X] Render grid lines between tiles for visual clarity
[X] Call `renderMap()` after world entry with zone and entity data from state

### Phase UI-3 Validation

[X] After login + enter world, canvas shows the Village Green terrain grid with correct colors
[X] Player marker visible at starting position
[X] NPCs (Elder Maren, Merchant Tova) and container (Old Chest) visible at their seeded positions
[X] Resizing the browser window re-renders correctly

---

## Phase UI-4: Movement & Interaction

Connect input to movement intents and entity inspection.

[X] Create `client/js/input.js` — keyboard listener for arrow keys and WASD, maps to direction strings
[X] Add mobile d-pad to `index.html` / `style.css` — four directional buttons in bottom-left corner, translucent
[X] Wire d-pad buttons to same movement handler as keyboard
[X] Movement handler: call `api.attemptMove(characterId, direction)` → on accepted, update state position + re-render map → on rejected, show toast with reason
[X] Refresh nearby entities after each successful move via `api.getNearbyEntities()`
[X] Add click/tap handler on canvas: translate pixel coordinates to tile coordinates, find entity at that tile
[X] Render entity inspect popup: show entity name, type, position; "Pick Up" button for items, "Loot" button for containers
[X] Wire "Pick Up" to `api.pickupItem()` → refresh map + inventory
[X] Wire "Loot" for containers: add looted items to inventory via `api.addItemToInventory()` for each loot entry

### Phase UI-4 Validation

[X] Arrow keys / WASD move the player on the map, camera follows
[X] Moving into walls shows "blocked by wall" toast
[X] D-pad buttons produce the same movement
[X] Clicking an NPC shows inspect popup with name and dialogue
[X] Clicking the Old Chest shows loot popup, looting adds items to inventory

---

## Phase UI-5: HUD

Add the persistent status overlay.

[X] Create `client/js/panels/hud.js` — `renderHud(state)` function
[X] Render character name and level, left-aligned in HUD container
[X] Render HP bar (green fill on dark background, numeric label)
[X] Render MP bar (blue fill)
[X] Render stamina bar (yellow fill)
[X] Fetch resources from `api.getCharacterResources()` on world entry
[X] Re-render HUD after any action that may change resources (equip, use consumable)

### Phase UI-5 Validation

[X] HUD visible at top of screen with correct character name, level, and bar values
[X] Bars show correct proportions (e.g. 100/100 = full bar)
[X] HUD is translucent, map visible behind it

---

## Phase UI-6: Character Panels

Build the slide-over panels for profile, inventory, equipment, and skills.

### Profile

[X] Create `client/js/panels/profile.js` — fetch from `api.getCharacterProfile()`, render name, level, XP, archetype, faction, biography
[X] Wire nav bar "Profile" button to toggle profile panel

### Inventory

[X] Create `client/js/panels/inventory.js` — fetch from `api.getInventory()`, render scrollable item list
[X] Each item row shows: name, category, quantity, "Equip" button (if equippable), "Drop" button
[X] Wire "Equip" to `api.equipItem()` → refresh inventory + equipment + HUD
[X] Wire "Drop" to `api.dropItem()` → refresh inventory + map (new item entity on ground)
[X] Wire nav bar "Inventory" button to toggle inventory panel

### Equipment

[X] Create `client/js/panels/equipment.js` — fetch from `api.getEquipment()` + `api.getCharacterAttributes()`
[X] Render slot list: slot name, equipped item name or "Empty", item stats, "Unequip" button
[X] Render attribute summary section: base stats, equipment bonuses, effective totals
[X] Wire "Unequip" to `api.unequipItem()` → refresh equipment + inventory + HUD
[X] Wire nav bar "Equipment" button to toggle equipment panel

### Skills

[X] Create `client/js/panels/skills.js` — fetch from `api.getCharacterSkills()`, render list or empty state message
[X] Wire nav bar "Skills" button to toggle skills panel

### Panel Behavior

[X] Only one panel open at a time — opening a panel closes any other
[X] Panel open/close has CSS transition (slide from right)
[X] Map is dimmed but visible behind open panel
[X] Close button on each panel header

### Phase UI-6 Validation

[X] Each nav button opens and closes its panel
[X] Profile shows correct character data
[X] Inventory lists items picked up from the Old Chest
[X] Equipping an item from inventory moves it to equipment panel and updates attributes
[X] Unequipping returns item to inventory
[X] Dropping an item removes it from inventory and shows it on the map
[X] Skills panel shows empty state gracefully

---

## Phase UI-7: Integration & Polish

Full flow testing and UX refinements.

[X] Add "Leave World" option in menu — calls `api.leaveWorld()`, returns to character select screen
[X] Toast messages for all action outcomes: move rejection, equip success/failure, pickup, drop, loot
[X] Toasts auto-dismiss after 2 seconds, stack vertically
[X] Disable movement input while a move request is in-flight (prevent rapid double-moves)
[X] Error toast for network failures: "Connection lost — please refresh"
[X] Verify mobile touch targets are at least 44px
[X] Test full end-to-end flow: login → create character → enter world → move around → loot container → equip weapon + armor → check attributes → drop item → pick it back up → view all panels → leave world → re-enter at saved position

### Phase UI-7 Validation

[X] All listed flow steps complete without errors
[X] Leave + re-enter preserves character position
[X] No console errors throughout the full flow
[X] Layout is usable on a 375px-wide viewport (phone)
