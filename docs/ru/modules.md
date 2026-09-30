# Справочник модулей

Публичный API каждого модуля. Сигнатуры соответствуют фактическому коду.

---

## `main.py` — точка входа

Запускает главный цикл. Создаёт игрового агента из `agent_config.json` (координаты, размер,
цвет, угол) с контроллером, выбранным через `create_controller()`. Подробное описание см. в
[architecture.md](architecture.md).

---

## `engine/settings.py` — конфигурация

Загружает все JSON-конфиги из `config/` и экспортирует константы.

| Функция | Назначение |
| --- | --- |
| `load_json(path)` | Загружает JSON-файл и возвращает dict |
| `load_named_config(name)` | Ищет имя файла конфигурации по `name` в `engine_config.json["engine"]`, загружает и возвращает его; выбрасывает `ValueError`, если имя не настроено |

Экспортируемые константы:

| Константа | Значение |
| --- | --- |
| `WINDOW_WIDTH`, `WINDOW_HEIGHT` | Размер окна (по умолчанию 800×600) |
| `FULLSCREEN` | Полноэкранный режим (по умолчанию `False`) |
| `FPS` | Ограничение FPS (по умолчанию `60`) |
| `TIMESCALE` | Множитель времени (по умолчанию `1.0`) |
| `DEBUG` | Включает отладочную панель (по умолчанию `False`) |
| `BACKGROUND_COLOR` | Цвет фона (по умолчанию чёрный) |
| `BORDER_COLOR` | Цвет границы мира (по умолчанию белый) |
| `GRID_SPACING` | Шаг сетки (по умолчанию `100`) |
| `WORLD_WIDTH`, `WORLD_HEIGHT` | Размер мира (по умолчанию 1000×1000) |
| `WORLD_TYPE` | Тип мира: `bounded` / `infinite` / `torus` |
| `AGENT_X`, `AGENT_Y` | Координаты появления агента (по умолчанию 100×200) |
| `AGENT_SIZE` | Размер агента (по умолчанию `20`) |
| `AGENT_COLOR` | Цвет агента (по умолчанию `(0, 255, 0)`) |
| `AGENT_LAYER` | Слой отрисовки агента (по умолчанию `0`) |
| `AGENT_ANGLE` | Начальное направление в градусах (по умолчанию `0`) |
| `AGENT_CONTROLLER` | Словарь конфигурации контроллера `{"name": ..., ...}` или `None` (агент без контроллера) |
| `CAMERA_MODE` | Режим камеры: `fixed` / `follow_agent` / `follow_food` |

> Примечание: файл объектов мира (`world_objects.json`) **не** загружается через `settings.py` —
> `main.py` читает его напрямую через `load_world_objects("config/world_objects.json")`.

---

## `engine/world.py` — класс `World`

| Метод | Назначение |
| --- | --- |
| `add_entity(entity)` | Добавляет сущность в мир |
| `update(dt)` | Для каждой сущности: `save_position()`, затем `entity.update(dt)` и `apply_world_rules()`; в конце вызывает `handle_collisions()` |
| `handle_collisions()` | Проверяет все пары объектов: при пересечении через `colliderect()` вызывает `on_collision()` с обеих сторон; удаляет мёртвые сущности |
| `apply_world_rules(entity)` | Применяет правила мира (ограничение для `bounded`, по модулю для `torus`, ничего для `infinite`) |
| `draw(surface, camera_offset)` | Сортирует сущности по `layer` и отрисовывает их; для torus — с дубликатами; для bounded — с границей |
| `get_wrapped_positions(entity)` | Возвращает список позиций (центр + 8 дубликатов по краям) для отрисовки в torus |

Атрибуты экземпляра: `width`, `height`, `type`, `entities`.

---

## `engine/entity.py` — сущности

### `Entity(x, y, layer, size=20, color=(255,255,255), tags=None)`

Базовый класс: `x`, `y`, `layer`, `size`, `color`, `tags` (множество), `is_alive`. Атрибут класса
`blocks_movement = False` (блокирует ли объект движение).

| Метод | Назначение |
| --- | --- |
| `update(dt)` | Заглушка, переопределяется в подклассах |
| `draw(surface, camera_offset=(0,0), override_position=None)` | Рисует квадрат `size × size` с центром в позиции |
| `get_rect()` | Возвращает `pygame.Rect` — физическую форму сущности (квадрат с центром в позиции). Используется системой коллизий |
| `save_position()` | Сохраняет текущую позицию как позицию начала кадра (`_prev_x`/`_prev_y`) |
| `revert_position()` | Восстанавливает `x`/`y` из позиции начала кадра, сохранённой `save_position()` |
| `on_collision(other, world)` | Реакция на столкновение; по умолчанию пустая, переопределяется в подклассах |
| `skip_collision_check()` | Возвращает `False`; эффекты могут переопределить на `True`, чтобы исключить объект из коллизий |

### `Food(x, y, size=10, color=(255,0,0), layer=0)`

Еда. Тег `{"food"}`. `update()` пустой. `on_collision()`: при попадании `Agent` даёт агенту
`+1 score` и исчезает (`is_alive = False`).

### `Obstacle(x, y, width, height, color=(100,100,100), layer=0)`

Прямоугольное препятствие. Передаёт в `Entity` `size = (width + height) // 2` (для совместимости) и
хранит собственные `width` / `height`. Тег `{"obstacle"}`. `blocks_movement = True`. Переопределяет
`draw()` и `get_rect()` под прямоугольную форму. `on_collision()` вызывает `revert_position()` у
другого объекта, отменяя его движение.

### `Agent(x, y, size=20, color=(0,255,0), layer=0, controller=None, angle=0)`

Агент. Тег `{"agent"}`. `update()` вызывает `self.controller.update(self, dt)`, если контроллер
задан. `draw()` дополнительно рисует жёлтую линию направления длиной `size * 1.5`. Атрибуты:
`score` (увеличивается при поедании еды).

### `ENTITY_REGISTRY`

Словарь `{"agent": Agent, "food": Food, "obstacle": Obstacle}` — используется при загрузке из JSON.

### `load_world_objects(filepath)`

Читает `{"objects": [...]}` из JSON. Для каждого объекта:

1. берёт `type` и ищет класс в `ENTITY_REGISTRY`; неизвестные типы пропускаются с
   предупреждением `[!] Unknown object type ...`;
2. передаёт остальные ключи конструктору как `**params`;
3. при ошибке создания выводит `[!] Failed to create ...` и продолжает работу.

---

## `engine/control.py` — контроллеры

### `Controller` (базовый)

`update(entity, dt)` выбрасывает `NotImplementedError` — это интерфейс. Подклассы явно объявляют
свой контракт двумя атрибутами класса:

* `params` — имена параметров конструктора, которые можно передать из конфигурации;
* `required_deps` — внешние зависимости (`"world"`, `"camera"`), внедряемые автоматически через
  `create_controller()`.

### `KeyboardController(speed=200)`

WASD: `W`/`S` — ось Y, `A`/`D` — ось X, скорость `speed` px/s.
Объявляет `params = ("speed",)` без зависимостей.

### `AIAgentController(world, speed=100)`

Движет сущность к ближайшей еде в `world.entities` (еда ищется по тегу `"food"`). Требует ссылку
на `world`: объявляет `params = ("speed",)` и
`required_deps = ("world",)`, поэтому создаётся через `create_controller({"name": "ai"}, world=...)`.

### `MouseController(speed=200, angular_speed=180, camera=None)`

Агент поворачивается к курсору и движется к нему — как ослик за морковкой. Экранные координаты
курсора переводятся в мировые с помощью смещения `camera` (камера внедряется автоматически
через `create_controller()`). Направление (`angle`) поворачивается к цели со скоростью
`angular_speed` град/с; движение ограничивается оставшейся дистанцией, поэтому агент
останавливается точно на курсоре. Объявляет `params = ("speed", "angular_speed")` и
`required_deps = ("camera",)`.

### `RotatingController(speed=200, angular_speed=180)`

`Q`/`E` — поворот со скоростью `angular_speed` град/с, `W` — вперёд, `S` — назад вдоль `angle`.
Объявляет `params = ("speed", "angular_speed")` без зависимостей.

### `CONTROLLER_REGISTRY`

Словарь `{"keyboard": KeyboardController, "mouse": MouseController, "ai": AIAgentController,
"rotate": RotatingController}` — сопоставляет имена контроллеров классам. Используется функцией
`create_controller()`.

### `create_controller(config=None, world=None, camera=None)`

Создаёт контроллер из имени (`"rotate"`) или словаря конфигурации вида
`{"name": "...", ...параметры конструктора}`. Возвращает `None` для `None` или пустого конфига
(агент без контроллера). Неизвестное имя выбрасывает `ValueError`. Параметры, не объявленные в
`params` контроллера, игнорируются (в stdout выводится предупреждение `[!]`). Зависимости,
объявленные в `required_deps`, внедряются автоматически: `"world"` (как у `AIAgentController`)
и `"camera"` (как у `MouseController`); при отсутствии зависимости — `ValueError`.

---

## `engine/camera.py` — класс `Camera`

`Camera(world, target=None, fixed_pos=(0,0))`

| Метод | Назначение |
| --- | --- |
| `set_mode(mode)` | Меняет режим камеры |
| `set_target(entity)` | Меняет цель |
| `update()` | Пересчитывает `offset` по режиму (`fixed` / `follow_agent` / `follow_food`) |
| `_find_nearest_food()` | Ищет еду, ближайшую к цели, по цвету `(255, 0, 0)` — временное решение, см. известные проблемы в [development.md](development.md) |

Атрибуты: `world`, `target`, `offset` (список `[x, y]`), `mode`, `fixed_pos`.

---

## `engine/ui.py` — отрисовка интерфейса

| Функция | Назначение |
| --- | --- |
| `draw_debug_panel(surface, agent, dt, world, clock)` | Полупрозрачная панель с координатами агента, FPS, количеством сущностей, `dt`, типом мира и `TIMESCALE`. Отрисовывается только при `DEBUG = True` |
| `draw_grid(surface, camera_offset, spacing=100, color=(50,50,50))` | Сетка, выровненная по камере (прокручивается вместе с миром) |

---

## `engine/utils.py` — утилиты

### `Timer(duration)`

Таймер на основе времени (в секундах): `duration`, `elapsed`, `active`.

| Метод | Назначение |
| --- | --- |
| `update(dt)` | Прибавляет `dt`, пока таймер активен |
| `is_done()` | `True`, если `elapsed >= duration` |
| `reset()` | Обнуляет `elapsed` и активирует таймер |
| `stop()` | Останавливает без сброса |
| `resume()` | Возобновляет |

### `StepCounter(max_steps=None)`

Счётчик дискретных шагов симуляции: `steps`, `max_steps`.

| Метод | Назначение |
| --- | --- |
| `increment(amount=1)` | Увеличивает счётчик |
| `is_done()` | `True`, если `max_steps` задан и `steps >= max_steps` |
| `reset()` | Обнуляет счётчик |