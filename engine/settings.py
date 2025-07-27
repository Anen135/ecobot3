# settings.py

import json
import os

def load_config(filename):
    path = os.path.join("config", filename)
    with open(path, "r") as f:
        return json.load(f)

# Configuration files
window_cfg = load_config("window_config.json")["window"]
world_cfg = load_config("world_config.json")["world"]
camera_cfg = load_config("camera_config.json")["camera"]
visual_cfg = load_config("visual_config.json")["visual"]

# Window settings
WINDOW_WIDTH = window_cfg["width"]
WINDOW_HEIGHT = window_cfg["height"]
FULLSCREEN = window_cfg["fullscreen"]

# FPS
FPS = visual_cfg["fps"]

# Vizual settings
BACKGROUND_COLOR = tuple(visual_cfg["background_color"])
BORDER_COLOR = tuple(visual_cfg["border_color"])
GRID_SPACING = visual_cfg.get("grid_spacing", 100)

# World settings
WORLD_WIDTH = world_cfg["width"]
WORLD_HEIGHT = world_cfg["height"]
WORLD_TYPE = world_cfg["type"]

# Camera settings
CAMERA_MODE = camera_cfg["mode"]

