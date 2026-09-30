from copy import deepcopy

from .camera import Camera
from .control import create_controller
from .entity import Agent, load_world_objects
from .generation import ProceduralWorldGenerator
from .world import World


class GameLoop:
    MODES = frozenset({"none", "regenerate", "restart_same"})

    def __init__(self, config, generation_config, agent_config, static_objects_path=None):
        if not isinstance(config, dict):
            raise TypeError("Game loop config must be an object")
        self.mode = config.get("mode", "none")
        if self.mode not in self.MODES:
            raise ValueError(f"Unknown game loop mode: {self.mode!r}")
        self.reset_agent_position = config.get("reset_agent_position", True)
        self.preserve_score = config.get("preserve_score", False)
        if not isinstance(self.reset_agent_position, bool) or not isinstance(self.preserve_score, bool):
            raise TypeError("reset_agent_position and preserve_score must be booleans")

        self.generation_config = deepcopy(generation_config)
        self.agent_config = deepcopy(agent_config)
        self.initial_seed = self.generation_config.get("seed", 0)
        self.static_objects = load_world_objects(static_objects_path) if static_objects_path else []
        self.round_number = 0
        self._create_world(previous_agent=None)

    def _create_world(self, previous_agent):
        world = World()
        for entity in deepcopy(self.static_objects):
            world.add_entity(entity)

        generation_config = deepcopy(self.generation_config)
        if self.mode == "regenerate":
            generation_config["seed"] = self.initial_seed + self.round_number
        for entity in ProceduralWorldGenerator(generation_config).generate(world):
            world.add_entity(entity)

        camera = Camera(world)
        if previous_agent is not None and not self.reset_agent_position:
            x, y, angle = previous_agent.x, previous_agent.y, previous_agent.angle
        else:
            x = self.agent_config.get("x", 100)
            y = self.agent_config.get("y", 200)
            angle = self.agent_config.get("angle", 0)

        agent = Agent(
            x=x,
            y=y,
            size=self.agent_config.get("size", 20),
            color=tuple(self.agent_config.get("color", [0, 255, 0])),
            layer=self.agent_config.get("layer", 0),
            angle=angle,
            controller=create_controller(self.agent_config.get("controller"), world=world, camera=camera),
        )
        if previous_agent is not None and self.preserve_score:
            agent.score = previous_agent.score
        world.add_entity(agent)
        camera.set_target(agent)
        camera.update()
        if previous_agent is not None:
            for entity in world.entities:
                if entity is not agent and "food" in entity.tags and world._entities_collide(agent, entity):
                    world.suppress_collision_until_separated(agent, entity)

        self.world = world
        self.camera = camera
        self.agent = agent

    def _has_food(self):
        return any(entity.is_alive and "food" in entity.tags for entity in self.world.entities)

    def update(self, dt):
        had_food = self._has_food()
        self.world.update(dt)
        if had_food and not self._has_food() and self.mode != "none":
            previous_agent = self.agent
            self.round_number += 1
            self._create_world(previous_agent)
