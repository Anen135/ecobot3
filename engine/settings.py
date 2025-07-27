import json
import os


CONFIG_DIR = "config" # Путь к директории с конфигурационными файлами
ENGINE_CONFIG_FILE = os.path.join(CONFIG_DIR, "engine_config.json") # Полный путь к главному конфигу движка

def load_json(path):
    with open(path, "r") as f:
        return json.load(f)

# Загрузка именованного конфига, указанного в engine_config
def load_named_config(name):
    if file := load_json(ENGINE_CONFIG_FILE)["engine"].get(name):
        return load_json(os.path.join(CONFIG_DIR, file))
    else:
        raise ValueError(f"No config file specified for '{name}' in engine_config.json")

# Загрузка конфигураций по категориям
engine_config = load_json(ENGINE_CONFIG_FILE)["system"]
window_cfg = load_named_config("window")["window"]
world_cfg = load_named_config("world")["world"]
camera_cfg = load_named_config("camera")["camera"]
visual_cfg = load_named_config("visual")["visual"]

# Параметры окна
WINDOW_WIDTH = window_cfg.get("width", 800)
WINDOW_HEIGHT = window_cfg.get("height", 600)
FULLSCREEN = engine_config.get("fullscreen", False)

# Параметры системы
FPS = engine_config.get("fps_limit", 60)
TIMESCALE = engine_config.get("timescale", 1.0)
DEBUG = engine_config.get("debug", False)

# Цвет фона (RGB), по умолчанию черный
BACKGROUND_COLOR = tuple(visual_cfg.get("background_color", [0, 0, 0]))
BORDER_COLOR = tuple(visual_cfg.get("border_color", [255, 255, 255]))
GRID_SPACING = visual_cfg.get("grid_spacing", 100)

# Параметры мира
WORLD_WIDTH = world_cfg.get("width", 1000)
WORLD_HEIGHT = world_cfg.get("height", 1000)
WORLD_TYPE = world_cfg.get("type", "bounded")

# Режим работы камеры (например, follow_agent, fixed и т.д.)
CAMERA_MODE = camera_cfg.get("mode", "follow_agent")
