# Configuration

All engine settings live in JSON files under `config/`. Loading is performed by
`engine/settings.py` at import time. Defaults come from the code (via `dict.get(key, default)`),
so optional fields may be omitted.

---

## `config/engine_config.json` — the main config

Has two sections:

### `"engine"` — named bindings to config files

| Key | Value | Used by |
| --- | --- | --- |
| `world` | world config file name | `load_named_config("world")` |
| `window` | window config file name | `load_named_config("window")` |
| `camera` | camera config file name | `load_named_config("camera")` |
| `visual` | visual config file name | `load_named_config("visual")` |
| `objects` | world objects file name | hardcoded in `main.py` as `config/world_objects.json` (the objects file is not loaded through `settings.py`) |

### `"system"` — system settings

| Key | Type | Default | Description |
| --- | --- | --- | --- |
| `fps_limit` | int | `60` | FPS limit |
| `debug` | bool | `false` | Enables the debug panel |
| `fullscreen` | bool | `false` | Fullscreen mode |
| `timescale` | float | `1.0` | Time multiplier (`dt` is multiplied by it) |

Current file example:

```json
{
    "engine": {
        "world": "world_config.json",
        "window": "window_config.json",
        "camera": "camera_config.json",
        "visual": "visual_config.json",
        "objects": "world_objects.json"
    },
    "system": {
        "fps_limit": 60,
        "debug": true,
        "fullscreen": false,
        "timescale": 1.0
    }
}
```

---

## `config/window_config.json` — window

| Key | Type | Default | Description |
| --- | --- | --- | --- |
| `width` | int | `800` | Window width in pixels |
| `height` | int | `600` | Window height in pixels |

---

## `config/world_config.json` — world

| Key | Type | Default | Description |
| --- | --- | --- | --- |
| `width` | int | `1000` | World width in pixels |
| `height` | int | `1000` | World height in pixels |
| `type` | string | `"bounded"` | World type: `bounded` (with borders), `infinite` (borderless), `torus` (wraparound) |

---

## `config/camera_config.json` — camera

| Key | Type | Default | Description |
| --- | --- | --- | --- |
| `mode` | string | `"follow_agent"` | Mode: `follow_agent`, `follow_food`, `fixed` |

---

## `config/visual_config.json` — visuals

| Key | Type | Default | Description |
| --- | --- | --- | --- |
| `background_color` | [int, int, int] | `[0, 0, 0]` | Background color (RGB) |
| `border_color` | [int, int, int] | `[255, 255, 255]` | World border color (only for `bounded`) |
| `grid_spacing` | int | `100` | Grid spacing in pixels |

---

## `config/world_objects.json` — world objects

Loaded in `main.py` via `load_world_objects()`. Format: an object with an `objects` array.
Each item has the required `type` field (a class name from `ENTITY_REGISTRY`) plus arbitrary
constructor parameters of that class.

Available types and parameters:

| `type` | Class | Parameters |
| --- | --- | --- |
| `agent` | `Agent` | `x`, `y`, `size=20`, `color=[0,255,0]`, `layer=0`, `controller`, `angle=0` |
| `food` | `Food` | `x`, `y`, `size=10`, `color=[255,0,0]`, `layer=0` |
| `obstacle` | `Obstacle` | `x`, `y`, `width`, `height`, `color=[100,100,100]`, `layer=0` |

`color` is given in JSON as an array of three numbers (R, G, B). Unknown types and objects
that fail to construct are skipped with a warning printed to stdout (see `load_world_objects`).

Example:

```json
{
    "objects": [
        { "type": "food", "x": 300, "y": 400 },
        { "type": "obstacle", "x": 600, "y": 600, "width": 100, "height": 50, "color": [150, 150, 255] }
    ]
}
```

---

## Loading rules

1. On import, `engine.settings` reads `engine_config.json` and then the named configs.
2. If a name is missing from the `"engine"` section, `load_named_config` raises `ValueError`.
3. Defaults are applied **only** when the key is absent from the JSON; an explicit `null` is
   passed through as-is and may break a constructor if it is not handled.