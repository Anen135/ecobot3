import json
import os


CONFIG_DIR = "config"
ENGINE_CONFIG_FILE = os.path.join(CONFIG_DIR, "engine_config.json")

def load_json(path):
    with open(path, "r") as f:
        return json.load(f)

def load_named_config(name):
    if file := load_json(ENGINE_CONFIG_FILE)["engine"].get(name):
        return load_json(os.path.join(CONFIG_DIR, file))
    else:
        raise ValueError(f"No config file specified for '{name}' in engine_config.json")

engine_config = load_json(ENGINE_CONFIG_FILE)["system"]
window_cfg = load_named_config("window")["window"]
world_cfg = load_named_config("world")["world"]
camera_cfg = load_named_config("camera")["camera"]
visual_cfg = load_named_config("visual")["visual"]

WINDOW_WIDTH = window_cfg.get("width", 800)
WINDOW_HEIGHT = window_cfg.get("height", 600)
FULLSCREEN = engine_config.get("fullscreen", False)

FPS = engine_config.get("fps_limit", 60)
TIMESCALE = engine_config.get("timescale", 1.0)
DEBUG = engine_config.get("debug", False)

BACKGROUND_COLOR = tuple(visual_cfg.get("background_color", [0, 0, 0]))
BORDER_COLOR = tuple(visual_cfg.get("border_color", [255, 255, 255]))
GRID_SPACING = visual_cfg.get("grid_spacing", 100)

WORLD_WIDTH = world_cfg.get("width", 1000)
WORLD_HEIGHT = world_cfg.get("height", 1000)
WORLD_TYPE = world_cfg.get("type", "bounded")

agent_cfg = load_named_config("agent")["agent"]
AGENT_X = agent_cfg.get("x", 100)
AGENT_Y = agent_cfg.get("y", 200)
AGENT_SIZE = agent_cfg.get("size", 20)
AGENT_COLOR = tuple(agent_cfg.get("color", [0, 255, 0]))
AGENT_LAYER = agent_cfg.get("layer", 0)
AGENT_ANGLE = agent_cfg.get("angle", 0)
AGENT_CONTROLLER = agent_cfg.get("controller")

GENERATION_CONFIG = load_named_config("generation")["generation"]

CAMERA_MODE = camera_cfg.get("mode", "follow_agent")
