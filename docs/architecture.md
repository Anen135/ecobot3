# Architecture

## Overview

The project is built around the **main game loop** in `main.py` and the `engine` package, in
which each subsystem lives in its own module:

* `settings.py` — the single point for loading configuration;
* `world.py` — the entity container and world rules;
* `entity.py` — the entity model and its registry;
* `control.py` — controllers (entity control);
* `camera.py` — a virtual camera with an `offset`;
* `ui.py` — grid and debug panel rendering;
* `utils.py` — helper classes (`Timer`, `StepCounter`).

Module dependencies:

```
main.py
  ├── engine.ui        (draw_grid, draw_debug_panel)
  ├── engine.settings  (configuration constants)
  ├── engine.world     (World)
  ├── engine.entity    (ENTITY_REGISTRY, load_world_objects, Agent)
  ├── engine.camera    (Camera)
  └── engine.control   (controllers)

engine.world    ──> engine.settings, engine.entity
engine.entity   ──> pygame
engine.camera   ──> engine.settings
engine.ui       ──> engine.settings
engine.control  ──> pygame
engine.settings ──> config/*.json
```

The `engine` package has no external dependencies besides `pygame` and the standard library
(`json`, `math`, `os`).

---

## Main loop (`main.py`)

Initialization sequence:

1. `pygame.init()` and window creation (size/fullscreen taken from the configuration).
2. Create an empty `World()`.
3. Load objects from `config/world_objects.json` via `load_world_objects()` and add them to the
   world with `world.add_entity()`.
4. Create an agent from `config/agent_config.json` (spawn coordinates, size, color, angle) with the
   controller selected via `create_controller()` — and add it to the world.
5. Create a camera — `Camera(world, target=agent)` (the mode comes from the configuration).

Per-frame main loop:

```
dt = (clock.tick(FPS) / 1000.0) * TIMESCALE     # delta time in seconds
process events (QUIT / ESC)                      # → exit the loop
world.update(dt)                                 # update() of every entity + world rules
camera.update()                                  # recompute the camera offset
screen.fill(BACKGROUND_COLOR)
ui.draw_grid(screen, camera.offset)              # scrollable grid
world.draw(screen, camera.offset)                # draw entities sorted by layer
ui.draw_debug_panel(screen, agent, dt, world, clock)  # only if DEBUG
pygame.display.flip()
```

**Important:** `dt` is the time elapsed since the previous frame (in seconds), multiplied by
`TIMESCALE` from the configuration. All entity movement must be scaled by `dt` so that speed does
not depend on FPS.

---

## Render layers

The draw order is determined by the entity's `layer` field. In `World.draw()` entities are sorted
by ascending `layer`:

| `layer` value | Purpose |
| --- | --- |
| `-1` | background |
| `0` | objects (default for `Food`, `Obstacle`, `Agent`) |
| `1+` | effects |

Entities have **two coordinate systems**:

* world coordinates `(x, y)` — the physical position of the entity;
* screen coordinates — `(x, y) - camera_offset`, computed when drawing.

The camera sets the `offset` so that the target entity ends up in the center of the screen.

---

## World and world rules

`World` (`engine/world.py`) stores the `entities` list and applies rules depending on `world.type`:

* **`infinite`** — no restrictions; `apply_world_rules()` returns immediately;
* **`bounded`** — entity coordinates are clamped to the world bounds, and a world border is drawn;
* **`torus`** — coordinates are taken modulo the world size; entities are drawn with edge
  duplicates via `get_wrapped_positions()`.

`World.update(dt)` calls `entity.update(dt)` for every entity, then `apply_world_rules(entity)`,
and at the end — `handle_collisions()`.

---

## Entity system

The base `Entity` class (`engine/entity.py`) holds: coordinates, `layer`, `size`, `color`,
`tags` (a set of string labels), and the `is_alive` flag.

Subclasses:

* `Food` — red food, tag `"food"`;
* `Obstacle` — a rectangular obstacle (`width` / `height`), tag `"obstacle"`;
* `Agent` — has `controller` and `angle` (direction in degrees, 0 = right); `update()` delegates
  control to the controller; draws a yellow direction line.

Types are registered in `ENTITY_REGISTRY = {"agent": Agent, "food": Food, "obstacle": Obstacle}`.
Loading objects from JSON (`load_world_objects`) uses this registry: the `"type"` field in JSON
determines the class; the remaining fields are passed to the constructor as keyword arguments
(the `"type"` field is removed from the parameters).

---

## Controllers

The `Controller.update(entity, dt)` interface — an entity calls its own controller from inside
its `update()`. Implementations:

| Controller | Control |
| --- | --- |
| `KeyboardController` | WASD — movement along the X/Y axes, speed in px/s |
| `RotatingController` | Q/E — rotation, W/S — forward/backward along `angle` |
| `MouseController` | turns and moves toward the cursor (like a donkey chasing a carrot) |
| `AIAgentController(world, ...)` | moves toward the nearest food (found by the `"food"` tag) |

The controller of the player agent is chosen in `config/agent_config.json` by name. Names are
registered in `CONTROLLER_REGISTRY`; `create_controller()` builds the instance (passing the
`world` and `camera` references to controllers that need them).

---

## Camera

`Camera` (`engine/camera.py`) computes `offset` depending on `camera.mode`:

* **`fixed`** — a fixed offset `fixed_pos` (0, 0);
* **`follow_agent`** — follows `target` (usually the agent), centering it;
* **`follow_food`** — follows the food closest to the target.

For `bounded` worlds the offset is clamped to the world bounds so the view never leaves the map.

---

## Collision system

Implemented per [collision_system.md](collision_system.md):

* `entity.on_collision(other, world)` — the reaction to a collision; each object decides for itself
  what to do (`Food` disappears when hit by an `Agent`, `Obstacle` cancels the other's movement);
* the `blocks_movement` flag — whether the object blocks movement (`True` for `Obstacle`);
* `World.handle_collisions()` — checks pairs via `colliderect()` and calls `on_collision()` from
  both sides; called from `World.update(dt)` after movement; dead entities are removed.

Optional extensions (circle collisions, layer/mask-based collisions, exit events) remain open.