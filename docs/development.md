# Developer Guide

## Environment

The project targets **Python 3.10+** (uses `:=`-expressions and type annotations).

The only external dependency is **Pygame**:

```
pip install pygame
```

The repository contains a local `venv/` (not committed). Run with it:

```
venv\Scripts\python.exe main.py      # Windows / PowerShell
```

## Running

```
python main.py
```

Controls (the default controller is `RotatingController`):

| Key | Action |
| --- | --- |
| `Q` / `E` | Rotate counterclockwise / clockwise |
| `W` / `S` | Move forward / backward along the current direction |
| `ESC` | Quit |

## Linting

`pyproject.toml` configures [ruff](https://docs.astral.sh/ruff/) (ignores `E701`, `I001`).
Run it before committing:

```
ruff check .
```

## Conventions

* Code comments and docstrings are written in **Russian** (project convention); the documentation
  in `docs/` is maintained **in English**.
* Speeds are given in pixels per second; all movement is multiplied by `dt`.
* The `layer` field: `-1` — background, `0` — objects, `1+` — effects.
* New entity types are registered in `ENTITY_REGISTRY` — then they can be loaded from JSON.
* Do not use an empty `pass` inside `apply_world_rules` (currently `return`, so sourcery does not complain).
* Debug output and panels go behind the `DEBUG` flag from the configuration.

## Known issues and notes

1. **`AIAgentController._find_closest_food()`** accesses `e.type`, but entities have no `type`
   field (they have `tags`). Using this controller raises an `AttributeError`. `main.py` uses
   `RotatingController` by default, so the bug is not triggered. Fix: filter by tags, e.g.
   `"food" in e.tags` (as in `tags={"food"}`).

2. **Food detection by color** — `Camera._find_nearest_food()` finds food as
   `e.color == (255, 0, 0)`. This is a color-guessing hack: if the food's color changes
   (constructor or JSON), the camera stops finding it. Better to filter by tags, as in item 1.

3. **World objects are not loaded via `settings`** — `main.py` hardcodes
   `"config/world_objects.json"` even though `engine_config.json` already has an `"objects"`
   binding. Loading objects via `load_named_config("objects")` would unify the configuration.

4. **No dependency file** — a `requirements.txt` / dependency section in `pyproject.toml` is
   missing, so the Pygame dependency is not pinned anywhere.

5. **Collision extensions are not implemented** — the base system (`on_collision` /
   `blocks_movement` / `handle_collisions`) is implemented per
   [collision_system.md](collision_system.md); optional extensions (circle collisions,
   collision layers/masks, exit events) remain open.

## Workflow

* The default branch is `main`. The commit history is in Russian.
* Update `docs/` in sync with the code.