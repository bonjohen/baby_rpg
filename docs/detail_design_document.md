# Mobile Shared-Map RPG Design Input

## Purpose

This document defines the first-pass product shape for a phone-based RPG in which multiple players share a common map and interact through a central game service. It is written as planning input for a software agent that will later decompose the system into implementation tasks, interfaces, modules, and storage design. The goal at this stage is not to define every game rule, but to establish a clean separation between user interface, application interface, and persistent data structures so the software can grow without major rework.

## Product Model

The application is a client-server multiplayer RPG. The phone application is responsible for presentation, local interaction flow, and temporary caching. The server is responsible for authority over the shared world, player state, item ownership, movement, combat validation, and synchronization between players. The client may predict or animate local actions for responsiveness, but the server remains the source of truth.

The product has two major user experiences. The first is character management, where the player views and adjusts character-related data such as profile, skills, equipment, inventory, and progression. The second is live play on a shared map, where the player sees terrain, nearby entities, and outcomes of actions that affect the shared world. These two experiences must feel connected, but they do not have the same technical requirements. Character pages can tolerate ordinary request-response behavior. The shared map requires persistent low-latency synchronization.

## User Interface

The phone application should be organized around a main game shell with a persistent navigation model. The map is the primary screen because it represents live play and shared context. Character profile, skills, equipment, inventory, and quest or journal pages are secondary views that can be opened from the shell without making the player feel they have exited the world. In practice, this means the app should behave more like a map-centered game with layered panels than like a collection of unrelated forms.

The login and character selection flow should be brief and stable. After authentication, the player selects or creates a character and enters the game shell. Once inside the shell, the default view is the shared map. The map screen should show the local terrain, visible objects, nearby players or NPCs, the player’s current status summary, and a small set of high-frequency actions such as movement, inspect, interact, and possibly attack or talk depending on the design direction. The map screen should avoid deep data density. Detailed information belongs in supporting pages.

The character profile page should expose identity and progression information. This includes character name, portrait or avatar reference, faction or class if used, level, experience, health and resource pools, major attributes, and high-level derived values. The purpose of this page is to answer “who is this character now” rather than to support active decision making during movement or combat.

The skills page should expose learnable and active capabilities. It should support browsing skill groups, inspecting prerequisites, viewing cooldown or cost information, and identifying which skills are currently equipped, learned, locked, or available for upgrade. This page is partly informational and partly transactional. The player needs to understand the current build and be able to make explicit choices that will later be validated and saved by the server.

The equipment page should model worn or equipped items using stable slot conventions. It should show what is currently equipped, the effect of each item on character performance, and whether a new item can legally replace an existing one. The page should support comparison because item changes are one of the most common RPG actions outside live movement.

The inventory page should handle carried items, stack quantities, filters, and actions such as use, equip, inspect, split, drop, and trade if trading is enabled. On a phone, inventory friction grows quickly, so the design should favor clear categories, short item summaries, and fast access to item details rather than trying to render a desktop-style grid with too much density.

The quest or journal page should expose tracked objectives, story state, and notable world discoveries. Even in an MVP, this page is useful because it anchors the player’s understanding of progress. It can also serve as a human-readable view over server-side state transitions.

The chat or social panel should be treated as a live companion to the map rather than a separate mode. It should support local chat, system messages, and interaction feedback such as item pickups, combat results, or zone events. This panel does not need to dominate the design, but it should be reachable without leaving the current location context.

Across all screens, the UI should distinguish between authoritative saved data and temporary local presentation state. For example, dragging an item toward an equipment slot is local interface state. The actual equipment change does not exist until the server accepts the action. The UI must therefore be prepared to display pending, accepted, rejected, and refreshed states cleanly.

## Application Interface

The application interface should be divided into two communication styles. Stable or slower-changing operations should use a request-response API. Live world interaction should use a persistent event-oriented connection. This split keeps the design understandable and allows the software agent to plan the system in layers.

The request-response interface handles authentication, account lookup, character list retrieval, character detail loading, inventory reads, equipment reads, skill reads, and any explicit mutation that does not require frame-level or near-frame-level interaction. This interface should also handle bootstrap data for entering the world, such as character identity, last known position, visible zone identifier, and any reference versions required by the client cache.

The persistent realtime interface handles movement intent, action intent, map visibility updates, nearby entity appearance and disappearance, chat messages, combat events, and server-driven notifications. The server should send an initial snapshot when a player enters a zone or reconnects, then send incremental updates after that. The client should not request the full world on every change. Instead, it should maintain a synchronized local view of the relevant area based on server events.

The application interface should be modeled around intent and result rather than direct database mutation. A client does not say “set my position to x and y.” It says “attempt move north one tile” or “attempt move to target coordinate.” The server then validates terrain, collisions, movement rules, action timing, and any game constraints before publishing the accepted result. The same principle applies to equipping items, learning skills, opening containers, and initiating combat. This will matter later when cheat resistance, replay logging, and deterministic rule handling become important.

The interface should also be version-aware. World data, item definitions, and skill definitions are partly static and may change between releases. The client should be able to report the content version it expects, and the server should be able to reject or adjust requests if the client is out of sync. That avoids subtle bugs where the client displays one item definition while the server applies another.

At the interface level, identifiers should be stable and opaque. Characters, items, zones, entities, and definitions should each have their own identifier space. The client should not infer meaning from the identifier itself. This keeps the model flexible and prevents accidental coupling between UI assumptions and backend storage.

## World Data Schema

World data should be separated into definition data and runtime instance data. Definition data describes what a world element is in the abstract. Runtime data describes what currently exists in the live shared world.

A world record represents the top-level container for a playable setting. It should include world_id, world_name, world_description, content_version, status, and created_at or updated_at metadata. A world contains one or more zones. A zone record represents a playable region or map segment and should include zone_id, world_id, zone_name, zone_type, width, height, coordinate_system, terrain_reference, spawn_rules_reference, and adjacency or transition metadata that indicates how movement between zones occurs.

Terrain should be stored as map content rather than embedded directly into the zone row. The terrain model can evolve, so the zone should reference a terrain payload or terrain asset version. For a tile-based MVP, each tile should conceptually expose position, terrain type, passability, movement cost, visibility behavior, and optional references to interactable content such as doors, chests, hazards, or scripted triggers. The planning agent may later choose a compact storage layout, but the schema should assume that terrain and interactables are distinct concepts.

A live world entity record represents anything present on the map at runtime. This includes players, NPCs, monsters, dropped items, containers, and temporary objects. It should include entity_id, world_id, zone_id, entity_type, definition_id if applicable, x, y, facing, visibility_state, state_blob, created_at, updated_at, and lifecycle_status. The state_blob is intentionally generic at this stage because live entities differ widely. A monster and a treasure chest should not be forced into the same rigid columns for everything. The more stable common fields should remain first-class columns, while specialized runtime state can live in a typed payload.

World event data should also be first-class. A world_event record should include event_id, world_id, zone_id if local, event_type, source_entity_id, target_entity_id when relevant, payload, occurred_at, and retention_policy. This allows the server to publish actions, support replay or debugging, and maintain short-lived or durable records of what happened. Not every event needs permanent storage, but the model should exist from the beginning.

## Item Data Schema

Item data should also be divided into definitions and owned instances. An item definition describes the canonical design of an item type. An item instance describes one concrete item that exists in player inventory, equipment, a container, or the world.

An item_definition record should include item_def_id, item_name, item_category, rarity, stackable_flag, max_stack_size, equipment_slot_rules, use_rules, weight, value, icon_ref, content_version, and description. It should also include a stats payload that describes what the item changes when equipped or used. For example, a weapon definition may affect attack range, damage type, or speed, while a consumable may restore health or apply a temporary status. Because item behavior can become complex, the schema should expect descriptive rule payloads rather than attempting to flatten all future item mechanics into fixed columns.

An item_instance record should include item_instance_id, item_def_id, owner_type, owner_id, quantity, condition_value if durability exists, bound_state if ownership restrictions exist, custom_state payload, created_at, and updated_at. The owner_type and owner_id pair allow the instance to be attached to a character, container, vendor, or world entity. This avoids duplicating ownership models for every location where an item can live.

If containers are used, a container model should not be treated as a special case of inventory only. A container can be modeled as an entity or object with its own identifier, with item instances assigned to that owner. This keeps inventory movement conceptually simple. Moving an item means changing owner_type, owner_id, quantity, and possibly position metadata if the item is dropped into the world.

Equipment should not duplicate item data. Instead, equipment is a relationship between a character and an item instance mapped to a slot. An equipment_assignment record should include character_id, slot_id, item_instance_id, equipped_at, and state. The slot rules come from item definitions and character rules, not from the assignment itself.

## Character Data Schema

Character data should separate identity, progression, build, inventory ownership, and live presence. A character record should include character_id, account_id, character_name, avatar_ref, world_id for current world, current_zone_id, last_saved_x, last_saved_y, level, experience, status, created_at, and updated_at. This record answers the question of which character belongs to which account and where that character last existed in durable terms.

A character_profile record should hold more expressive or optional identity fields such as biography text, faction, class or archetype, origin, and presentation metadata. This can remain separate from the core character record so the main persistence path stays stable and compact.

A character_attributes record should include character_id and the major persistent values that define growth, such as strength, agility, intellect, endurance, willpower, or any game-specific equivalents. Derived combat values should usually not be stored unless they are needed for audit or optimization. They can be computed from base attributes, equipment, statuses, and skill effects. The schema should still permit a materialized summary view if performance later requires it.

A character_resources record should include character_id, health_current, health_max, mana_current or energy_current if relevant, mana_max or energy_max, stamina_current if used, and updated_at. These values change frequently enough that they should not be mixed carelessly into a broader profile payload.

A character_skill record should model one row per learned or partially learned skill. It should include character_id, skill_def_id, learned_state, rank, slot_assignment if skills can be actively equipped, progression_state payload, and updated_at. Skill definitions themselves belong to static content, not player state.

A character_inventory view can be built from item_instance ownership, but an explicit helper structure may still be useful during implementation. The important conceptual point is that inventory ownership belongs to item instances, not duplicated character rows. The character owns the items by relationship.

A character_status_effect record should include character_id, effect_def_id, source_entity_id if known, stacks, started_at, expires_at, and state payload. This supports buffs, debuffs, poison, cooldown markers, and temporary states without overloading the base resource model.

A live_presence record should represent the runtime participation of the character in the active world session. It should include character_id, session_id, entity_id, zone_id, x, y, facing, connection_state, last_heartbeat_at, and visibility_context. This is not purely durable game progression data. It is session-aware runtime state that allows reconnect logic and nearby-player synchronization.

## Relationships Between World, Item, and Character Data

The central relationship is that a character has a runtime representation in the world as an entity. The character record is durable identity and progression. The live entity record is the current world presence. They should be linked, but not collapsed into one object. This allows a character to exist in the database even when offline, while the world entity exists only when the character is active or when a retained representation is needed.

Items bridge character and world data. An item instance may be owned by a character, equipped by a character, stored in a container, or represented as a dropped object in the world. The item definition remains constant, while the item instance changes location and state over time. That makes item transfer, loot, vendor logic, and drops all variations of the same ownership model rather than entirely different systems.

World definitions constrain what characters and items can do. Zones determine legal positions. Terrain determines whether movement is possible. Interactables determine where items may be found or used. Skill and item definitions determine what a character can attempt. The application interface should therefore be understood as a layer that turns client intent into validated state transitions across these connected schemas.

## Recommended MVP Boundary

For the first implementation boundary, the data model should support one world, a small number of zones, one active character per account session, item definitions with basic equipment and consumables, character attributes and skills, inventory ownership, live position in a zone, and nearby-entity synchronization. Combat can be introduced after movement and world interaction are stable, because the same intent-validation-result model will already be in place.

The software agent planning the build should treat the UI shell, request-response API, realtime event channel, and the world-character-item schema as four coordinated tracks. The client should never directly model itself as authoritative for shared state. The server should always own the official state transitions, with the client optimized for clear presentation, responsive interaction, and recovery from latency or reconnection.
