# Конфигурация

Все настройки движка хранятся в JSON-файлах в папке `config/`. Загрузку выполняет
`engine/settings.py` в момент импорта. Значения по умолчанию берутся из кода (через `dict.get(key, default)`),
поэтому необязательные поля можно опускать.

---

## `config/engine_config.json` — главный конфиг

Содержит две секции:

### `"engine"` — именованные привязки к файлам конфигурации

| Ключ | Значение | Используется в |
| --- | --- | --- |
| `world` | имя файла конфигурации мира | `load_named_config("world")` |
| `window` | имя файла конфигурации окна | `load_named_config("window")` |
| `camera` | имя файла конфигурации камеры | `load_named_config("camera")` |
| `visual` | имя файла конфигурации визуализации | `load_named_config("visual")` |
| `objects` | имя файла объектов мира | жёстко прописано в `main.py` как `config/world_objects.json` (файл объектов загружается не через `settings.py`) |

### `"system"` — системные настройки

| Ключ | Тип | По умолчанию | Описание |
| --- | --- | --- | --- |
| `fps_limit` | int | `60` | Ограничение FPS |
| `debug` | bool | `false` | Включает отладочную панель |
| `fullscreen` | bool | `false` | Полноэкранный режим |
| `timescale` | float | `1.0` | Множитель времени (на него умножается `dt`) |

Пример текущего файла:

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

## `config/window_config.json` — окно

| Ключ | Тип | По умолчанию | Описание |
| --- | --- | --- | --- |
| `width` | int | `800` | Ширина окна в пикселях |
| `height` | int | `600` | Высота окна в пикселях |

---

## `config/world_config.json` — мир

| Ключ | Тип | По умолчанию | Описание |
| --- | --- | --- | --- |
| `width` | int | `1000` | Ширина мира в пикселях |
| `height` | int | `1000` | Высота мира в пикселях |
| `type` | string | `"bounded"` | Тип мира: `bounded` (с границами), `infinite` (без границ), `torus` (с зацикливанием) |

---

## `config/camera_config.json` — камера

| Ключ | Тип | По умолчанию | Описание |
| --- | --- | --- | --- |
| `mode` | string | `"follow_agent"` | Режим: `follow_agent`, `follow_food`, `fixed` |

---

## `config/visual_config.json` — визуализация

| Ключ | Тип | По умолчанию | Описание |
| --- | --- | --- | --- |
| `background_color` | [int, int, int] | `[0, 0, 0]` | Цвет фона (RGB) |
| `border_color` | [int, int, int] | `[255, 255, 255]` | Цвет границы мира (только для `bounded`) |
| `grid_spacing` | int | `100` | Шаг сетки в пикселях |

---

## `config/world_objects.json` — объекты мира

Загружается в `main.py` через `load_world_objects()`. Формат: объект с массивом `objects`.
Каждый элемент содержит обязательное поле `type` (имя класса из `ENTITY_REGISTRY`) и произвольные
параметры конструктора этого класса.

Доступные типы и параметры:

| `type` | Класс | Параметры |
| --- | --- | --- |
| `agent` | `Agent` | `x`, `y`, `size=20`, `color=[0,255,0]`, `layer=0`, `controller`, `angle=0` |
| `food` | `Food` | `x`, `y`, `size=10`, `color=[255,0,0]`, `layer=0` |
| `obstacle` | `Obstacle` | `x`, `y`, `width`, `height`, `color=[100,100,100]`, `layer=0` |

`color` указывается в JSON как массив из трёх чисел (R, G, B). Неизвестные типы и объекты,
которые не удалось создать, пропускаются с предупреждением в stdout (см. `load_world_objects`).

Пример:

```json
{
    "objects": [
        { "type": "food", "x": 300, "y": 400 },
        { "type": "obstacle", "x": 600, "y": 600, "width": 100, "height": 50, "color": [150, 150, 255] }
    ]
}
```

---

## Правила загрузки

1. При импорте `engine.settings` читает `engine_config.json`, а затем именованные конфиги.
2. Если имя отсутствует в секции `"engine"`, `load_named_config` выбрасывает `ValueError`.
3. Значения по умолчанию применяются **только** при отсутствии ключа в JSON; явный `null`
   передаётся как есть и может сломать конструктор, если он его не обрабатывает.