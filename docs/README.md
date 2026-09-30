# ecobot3 — Internal Documentation

Internal documentation for **ecobot3**, a 2D engine/sandbox built with Python and Pygame.
These docs are intended for developers of the project: they describe the architecture,
modules, configuration, and development plans.

---

## About the project

ecobot3 is an experiment in implementing a minimal 2D engine with an extensible architecture:

* **World** — a collection of entities (`Entity`) with support for three world types: `bounded` (with borders), `infinite` (borderless), and `torus` (wraparound).
* **Entities** — the base `Entity` class plus ready-made types: `Agent`, `Food`, `Obstacle`. New types are registered in `ENTITY_REGISTRY` and can be loaded from JSON configuration.
* **Controllers** — pluggable entity control: keyboard (WASD), mouse, AI (move toward food), rotate (Q/E + W/S).
* **Camera** — `follow_agent`, `follow_food`, and `fixed` modes, with boundary clamping for bounded worlds.
* **Configuration** — all settings are kept in JSON files under `config/` and loaded through `engine.settings`.

> The codebase (code comments, docstrings, commit messages) is written in Russian;
> this documentation is maintained in English.

---

## Repository structure

```
ecobot3/
├── main.py                  # Entry point and main game loop
├── pyproject.toml           # Tool settings (ruff)
├── TODO.md                  # Technical specification / roadmap
├── config/                  # Engine JSON configuration
│   ├── engine_config.json   #   main config (system + named file bindings)
│   ├── window_config.json   #   window settings
│   ├── world_config.json    #   world settings
│   ├── camera_config.json   #   camera settings
│   ├── visual_config.json   #   visual settings
│   ├── agent_config.json    #   player agent: spawn parameters and controller
│   └── world_objects.json   #   objects loaded into the world
├── engine/                  # Engine package
│   ├── __init__.py
│   ├── settings.py          #   configuration loading and export
│   ├── world.py             #   World class
│   ├── entity.py            #   Entity, Food, Obstacle, Agent, registry, JSON loading
│   ├── control.py           #   controllers
│   ├── camera.py            #   Camera class
│   ├── ui.py                #   debug panel and grid
│   └── utils.py             #   Timer, StepCounter
└── docs/                    # Internal documentation (this folder)
```

---

## Documents

| Document | Description |
| --- | --- |
| [architecture.md](architecture.md) | Architecture, main loop, data flow, render layers |
| [modules.md](modules.md) | Module reference and public API |
| [configuration.md](configuration.md) | All configuration files: keys, types, defaults |
| [development.md](development.md) | Setup, running, conventions, known issues |
| [collision_system.md](collision_system.md) | Specification of the planned collision system |

---

## Project status

| Area | Status |
| --- | --- |
| Configuration loading (`settings.py`) | ✅ Implemented |
| Entities, registry, JSON loading | ✅ Implemented |
| Worlds `bounded` / `infinite` / `torus` | ✅ Implemented |
| Controllers (keyboard, mouse, AI, rotate) | ✅ Implemented |
| Camera (3 modes) | ✅ Implemented |
| UI: debug panel, grid | ✅ Implemented |
| Utilities `Timer`, `StepCounter` | ✅ Implemented |
| **Collision system** (`on_collision`, `blocks_movement`, `handle_collisions`) | ✅ Implemented — see [collision_system.md](collision_system.md) |

The detailed collision-system plan lives in [TODO.md](../TODO.md) and is reproduced in
[collision_system.md](collision_system.md).