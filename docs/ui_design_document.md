# UI Design Document — Game Shell

## Purpose

This document defines the user interface for the Baby RPG client. It describes the visual structure, interaction model, rendering approach, and screen-by-screen behavior of a browser-based game shell that communicates with the existing FastAPI server. The goal is to establish clear decisions about layout, navigation, rendering technology, and state handling so the implementation can proceed without ambiguity.

## Technology Choices

The client is vanilla JavaScript with no framework or build toolchain. The tile map is rendered on an HTML5 Canvas element. All other UI — panels, forms, navigation, HUD — is standard DOM with CSS. The client is served as static files by the same FastAPI process that hosts the API, so there is no separate frontend server and no CORS configuration needed in production.

These choices follow from the project constraints. The game shell is a single-page application where most visual complexity lives in a canvas-rendered map. Panels are infrequent, layout-oriented surfaces that benefit from standard DOM flow. A framework would add dependency weight without meaningful benefit for this structure.

No external art assets are required. Terrain tiles are colored rectangles. Entities are simple geometric shapes differentiated by color and form. This allows the full UI to function without a sprite pipeline while remaining visually clear enough to demonstrate all game behaviors.

## Application Shell

The shell is the persistent container that remains on screen for the entire session after login. It has three layers stacked in z-order:

1. **Map canvas** — fills the viewport, renders terrain and entities.
2. **HUD overlay** — anchored to the top of the screen, translucent, always visible during gameplay. Shows character name, level, and resource bars (HP, MP, stamina).
3. **Panel layer** — slide-over panels that appear from the right or bottom when activated. Panels cover most of the map but do not replace it. The player can dismiss a panel to return to the map without any navigation transition.

A bottom navigation bar is fixed at the screen edge and provides buttons for: Profile, Inventory, Equipment, Skills, and a Menu/Settings toggle. The nav bar is always visible during gameplay. Tapping a nav button opens the corresponding panel; tapping it again or tapping a close control dismisses the panel.

The login and character selection screens replace the shell entirely. Once the player enters the world, the shell takes over and login UI is removed from the DOM.

## Screen Descriptions

### Login Screen

A simple centered form with username and password fields and a Login button. On successful authentication, the screen transitions to the character selection view. There is no registration flow — the stub auth endpoint creates accounts on first login, so the same form handles both cases.

### Character Selection Screen

Displays after login. Shows a list of existing characters for the account as selectable cards showing name, level, and archetype. Below the list, a "Create Character" section with a name input and archetype selector. Selecting an existing character calls `enter_world` and transitions to the game shell. Creating a character calls `create_character`, then `enter_world`.

If the account has no characters, only the creation form is shown.

### Map Screen

The map is the primary gameplay surface. It occupies the full viewport behind the HUD and nav bar.

**Terrain rendering.** The canvas draws a grid of colored squares, one per tile. Each terrain type has a fixed fill color:

| Terrain | Color | Passable |
|---------|-------|----------|
| grass | #4a7c40 | yes |
| wall | #6b6b6b | no |
| water | #3a6ea5 | no |
| tree | #2d5a1e | no |
| stone | #a08060 | yes |

Tile size is calculated dynamically to fill the canvas while maintaining square aspect ratio. A minimum tile size of 32px is enforced; if the zone is larger than the viewport can display at that size, the viewport scrolls to keep the player centered.

**Entity rendering.** Entities are drawn on top of terrain tiles. Each entity type has a distinct shape and color:

| Entity Type | Shape | Color |
|-------------|-------|-------|
| player | filled circle | #f0c040 (gold) |
| npc | filled circle | #40a0f0 (blue) |
| container | filled square | #c07020 (brown) |
| item | filled diamond | #e04080 (pink) |

The player entity is always rendered last so it appears on top. A thin black outline on all entity shapes provides contrast against terrain.

**Viewport.** The camera centers on the player. If the zone fits entirely within the canvas, it is centered with a dark background fill around the edges. If the zone is larger, the viewport scrolls so the player is centered with a margin of at least 3 tiles visible in each direction when possible.

**Entity interaction.** Clicking or tapping on a tile occupied by a non-player entity opens an inspect popup. The popup shows the entity's name (from state_blob), type, and position. For containers, a "Loot" button appears. For dropped items, a "Pick Up" button appears. The popup dismisses on outside click or an explicit close button.

### HUD

The HUD is a fixed-position overlay at the top of the map screen. It is translucent so terrain is partially visible behind it. It contains:

- Character name and level (left-aligned)
- Health bar (red/green, shows current/max)
- Mana bar (blue, shows current/max)
- Stamina bar (yellow, shows current/max)

Bars are horizontal, stacked vertically, and show numeric values as text centered on the bar. The HUD refreshes on world entry and after any action that may change resources.

### Profile Panel

Slides over the map from the right. Displays:

- Character name, level, experience (with progress to next level)
- Archetype and faction
- Biography (if set)
- Origin

Fetches from `GET /characters/{id}/profile`. Read-only in the MVP.

### Inventory Panel

Slides over the map. Displays a scrollable list of items owned by the character. Each row shows:

- Item name
- Category icon or label (weapon, armor, consumable)
- Quantity (if stackable)
- Action buttons: "Equip" (if equippable), "Drop"

"Equip" calls `POST /characters/{id}/equip` with the item instance ID and the first allowed slot from the item definition. On success, the panel refreshes and the HUD updates if stats changed.

"Drop" calls `POST /characters/{id}/inventory/{item_id}/drop`. On success, the item disappears from the list and appears as an entity on the map.

Fetches from `GET /characters/{id}/inventory`.

### Equipment Panel

Slides over the map. Displays equipment slots in a vertical list:

- Slot name (head, chest, legs, feet, main_hand, off_hand)
- Equipped item name or "Empty"
- Item stats if equipped
- "Unequip" button for occupied slots

Below the slot list, a summary section shows base attributes and equipment-derived bonuses, fetched from `GET /characters/{id}/attributes`.

Fetches slot data from `GET /characters/{id}/equipment`.

### Skills Panel

Slides over the map. Displays a list of learned skills with rank and slot assignment. In the MVP this list will be empty since no skill definitions are seeded, but the panel structure and fetch logic are in place.

Fetches from `GET /characters/{id}/skills`.

### Mobile D-Pad

On touch devices (or always, since there is no detection requirement), a directional pad is rendered in the bottom-left corner of the map screen, above the nav bar. Four arrow buttons arranged in a cross pattern send movement intents for north, south, east, and west. The d-pad is translucent and does not obstruct the map significantly.

On desktop, arrow keys and WASD serve the same function. Both input methods are always active.

### Toast Messages

A toast area in the bottom-center of the screen (above the nav bar, below the d-pad) shows brief feedback messages that auto-dismiss after 2 seconds. Examples:

- "Cannot move: blocked by wall"
- "Picked up Iron Sword"
- "Equipped Leather Tunic to chest"
- "Too far away to pick up"

Toasts stack vertically if multiple appear in quick succession, with older toasts fading out.

## State Management

The client maintains a local state object that holds:

- **Session**: session_token, account_id
- **Character**: character_id, entity_id, full character detail
- **Zone**: zone_id, width, height, tile grid (2D array of terrain data)
- **Entities**: list of nearby entities, refreshed after movement
- **Panel state**: which panel is currently open (at most one at a time)

State is populated from server responses and never persisted to local storage. On page refresh, the user returns to the login screen. The server holds all durable state.

The client distinguishes between confirmed state (from server responses) and pending state (user has initiated an action but no response yet). During a pending move, the player marker may show a directional indicator but does not change position until the server confirms. If the server rejects, the marker stays in place and a toast explains why.

## Navigation Flow

```
Login Screen
    ↓ (authenticate)
Character Select Screen
    ↓ (select or create + enter_world)
Game Shell
    ├── Map (always visible)
    ├── HUD (always visible)
    ├── Nav Bar (always visible)
    │   ├── Profile → Profile Panel (toggle)
    │   ├── Inventory → Inventory Panel (toggle)
    │   ├── Equipment → Equipment Panel (toggle)
    │   ├── Skills → Skills Panel (toggle)
    │   └── Menu → Leave World
    └── Entity Popup (on map click)
```

Only one panel can be open at a time. Opening a panel closes any other open panel. The map continues to be visible (dimmed) behind open panels.

## Server Communication

All communication uses the existing REST API via `fetch()`. There is no WebSocket connection in the MVP. The client polls for entity updates after each movement action rather than receiving push updates.

Every mutating action (move, equip, drop, pickup) follows the intent-result pattern:

1. Client sends intent to server
2. Client enters pending state (disables repeat input for that action)
3. Server responds with accepted or rejected
4. Client updates local state from the response
5. Client refreshes any affected UI (map, HUD, panel)

Failed requests show an error toast. Network errors show "Connection lost — please refresh."
