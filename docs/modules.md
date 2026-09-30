# Module Reference

The public API of every module. Signatures follow the actual code.

---

## `main.py` — entry point

Runs the main loop. Creates the player agent from `agent_config.json` (coordinates, size, color,
angle) with the controller selected via `create_controller()`. See [architecture.md](architecture.md)
for a detailed description.

---

## `engine/settings.py` — configuration

Loads all JSON configs from `config/` and exports constants.

| Function | Purpose |
| --- | --- |
| `load_json(path)` | Loads a JSON file and returns a dict |
| `load_named_config(name)` | Looks up the config file name in `engine_config.json["engine"]` by `name`, loads and returns it; raises `ValueError` if the name is not configured |

Exported constants:

| Constant | Meaning |
| --- | --- |
| `WINDOW_WIDTH`, `WINDOW_HEIGHT` | Window size (default 800×600) |
| `FULLSCREEN` | Fullscreen mode (default `False`) |
| `FPS` | FPS limit (default `60`) |
| `TIMESCALE` | Time multiplier (default `1.0`) |
| `DEBUG` | Enables the debug panel (default `False`) |
| `BACKGROUND_COLOR` | Background color (default black) |
| `BORDER_COLOR` | World border color (default white) |
| `GRID_SPACING` | Grid spacing (default `100`) |
| `WORLD_WIDTH`, `WORLD_HEIGHT` | World size (default 1000×1000) |
| `WORLD_TYPE` | World type: `bounded` / `infinite` / `torus` |
| `AGENT_X`, `AGENT_Y` | Agent spawn coordinates (default 100×200) |
| `AGENT_SIZE` | Agent size (default `20`) |
| `AGENT_COLOR` | Agent color (default `(0, 255, 0)`) |
| `AGENT_LAYER` | Agent render layer (default `0`) |
| `AGENT_ANGLE` | Initial direction in degrees (default `0`) |
| `AGENT_CONTROLLER` | Controller config dict `{"name": ..., ...}` or `None` (agent without a controller) |
| `CAMERA_MODE` | Camera mode: `fixed` / `follow_agent` / `follow_food` |

> Note: the world objects file (`world_objects.json`) is **not** loaded through `settings.py` —
> `main.py` reads it directly via `load_world_objects("config/world_objects.json")`.

---

## `engine/world.py` — the `World` class

| Method | Purpose |
| --- | --- |
| `add_entity(entity)` | Adds an entity to the world |
| `update(dt)` | For every entity: `save_position()`, then `entity.update(dt)` and `apply_world_rules()`; at the end calls `handle_collisions()` |
| `handle_collisions()` | Checks all entity pairs: on `colliderect()` overlap calls `on_collision()` from both sides; removes dead entities |
| `apply_world_rules(entity)` | Applies world rules (clamp for `bounded`, modulo for `torus`, nothing for `infinite`) |
| `draw(surface, camera_offset)` | Sorts entities by `layer` and draws them; torus — with duplicates; bounded — with a border |
| `get_wrapped_positions(entity)` | Returns a list of positions (center + 8 edge copies) for torus rendering |

Instance attributes: `width`, `height`, `type`, `entities`.

---

## `engine/entity.py` — entities

### `Entity(x, y, layer, size=20, color=(255,255,255), tags=None)`

Base class: `x`, `y`, `layer`, `size`, `color`, `tags` (a set), `is_alive`. Class attribute
`blocks_movement = False` (whether the object blocks movement).

| Method | Purpose |
| --- | --- |
| `update(dt)` | Stub to be overridden |
| `draw(surface, camera_offset=(0,0), override_position=None)` | Draws a `size × size` square centered on the position |
| `get_rect()` | Returns a `pygame.Rect` — the entity's physical shape (centered square). Used by the collision system |
| `save_position()` | Saves the current position as the frame-start position (`_prev_x`/`_prev_y`) |
| `revert_position()` | Restores `x`/`y` from the frame-start position saved by `save_position()` |
| `on_collision(other, world)` | Reaction to a collision; empty by default, overridden in subclasses |
| `skip_collision_check()` | Returns `False`; effects can override it to `True` to exclude the object from collisions |

### `Food(x, y, size=10, color=(255,0,0), layer=0)`

Food. Tag `{"food"}`. `update()` is empty. `on_collision()`: when hit by an `Agent`, gives the agent
`+1 score` and disappears (`is_alive = False`).

### `Obstacle(x, y, width, height, color=(100,100,100), layer=0)`

A rectangular obstacle. Passes `size = (width + height) // 2` to `Entity` (for compatibility) and
keeps its own `width` / `height`. Tag `{"obstacle"}`. `blocks_movement = True`. Overrides `draw()`
and `get_rect()` for the rectangle shape. `on_collision()` calls `revert_position()` on the other
object, canceling its movement.

### `Agent(x, y, size=20, color=(0,255,0), layer=0, controller=None, angle=0)`

Agent. Tag `{"agent"}`. `update()` calls `self.controller.update(self, dt)` when a controller is
set. `draw()` additionally renders a yellow direction line of length `size * 1.5`. Attributes:
`score` (incremented when food is eaten).

### `ENTITY_REGISTRY`

Dict `{"agent": Agent, "food": Food, "obstacle": Obstacle}` — used when loading from JSON.

### `load_world_objects(filepath)`

Reads `{"objects": [...]}` from JSON. For each object:

1. takes `type` and looks up the class in `ENTITY_REGISTRY`; unknown types are skipped with a
   `[!] Unknown object type ...` warning;
2. passes the remaining keys to the constructor as `**params`;
3. on construction failure prints `[!] Failed to create ...` and continues.

---

## `engine/control.py` — controllers

### `Controller` (base)

`update(entity, dt)` raises `NotImplementedError` — an interface.

### `KeyboardController(speed=200)`

WASD: `W`/`S` — Y axis, `A`/`D` — X axis, speed `speed` px/s.

### `AIAgentController(world, speed=100)`

Moves the entity toward the nearest food in `world.entities` (food is searched by the `"food"`
tag). Requires a `world` reference; created by the `ai` branch of `create_controller()` with
`world=...`.

### `MouseController(speed=200, angular_speed=180, camera=None)`

The agent turns toward the cursor and moves to it — like a donkey chasing a carrot. Screen cursor
coordinates are converted to world ones using the `camera` offset (the camera is passed by the
`mouse` branch of `create_controller()`). The heading (`angle`) rotates toward the target at
`angular_speed` deg/s; movement is clamped to the remaining distance, so the agent stops exactly
on the cursor.

### `RotatingController(speed=200, angular_speed=180)`

`Q`/`E` — rotate at `angular_speed` deg/s, `W` — forward, `S` — backward along `angle`.

### `create_controller(config=None, world=None, camera=None)` — factory

Creates a controller: the `name` from the config selects a branch that constructs the class
directly, reading only the parameters it needs (extra config keys are ignored). `config` can be a
controller name (`"rotate"`) or a dict `{"name": "...", ...params}`; `None` or an empty config
returns `None` (agent without a controller). Unknown names raise `ValueError`. The factory takes
`world` and `camera` as arguments and passes them to the branches that require them: `world` for
`ai`, `camera` for `mouse`; a missing required reference raises `ValueError`.

---

## `engine/camera.py` — the `Camera` class

`Camera(world, target=None, fixed_pos=(0,0))`

| Method | Purpose |
| --- | --- |
| `set_mode(mode)` | Changes the camera mode |
| `set_target(entity)` | Changes the target |
| `update()` | Recomputes `offset` by mode (`fixed` / `follow_agent` / `follow_food`) |
| `_find_nearest_food()` | Finds the food closest to the target by color `(255, 0, 0)` — a temporary solution, see known issues in [development.md](development.md) |

Attributes: `world`, `target`, `offset` (a list `[x, y]`), `mode`, `fixed_pos`.

---

## `engine/ui.py` — interface rendering

| Function | Purpose |
| --- | --- |
| `draw_debug_panel(surface, agent, dt, world, clock)` | A semi-transparent panel with the agent coordinates, FPS, entity count, `dt`, world type, and `TIMESCALE`. Drawn only when `DEBUG = True` |
| `draw_grid(surface, camera_offset, spacing=100, color=(50,50,50))` | Camera-aligned grid (scrolls together with the world) |

---

## `engine/utils.py` — utilities

### `Timer(duration)`

A time-based timer (seconds): `duration`, `elapsed`, `active`.

| Method | Purpose |
| --- | --- |
| `update(dt)` | Adds `dt` while the timer is active |
| `is_done()` | `True` if `elapsed >= duration` |
| `reset()` | Zeroes `elapsed` and activates the timer |
| `stop()` | Stops without resetting |
| `resume()` | Resumes |

### `StepCounter(max_steps=None)`

A counter of discrete simulation steps: `steps`, `max_steps`.

| Method | Purpose |
| --- | --- |
| `increment(amount=1)` | Increments the counter |
| `is_done()` | `True` if `max_steps` is set and `steps >= max_steps` |
| `reset()` | Zeroes the counter |