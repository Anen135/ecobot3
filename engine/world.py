# world.py

import random  # noqa: F401
from .settings import WORLD_WIDTH, WORLD_HEIGHT, WORLD_TYPE
from .entity import Entity  # noqa: F401

class World:
    def __init__(self):
        self.width = WORLD_WIDTH
        self.height = WORLD_HEIGHT
        self.type = WORLD_TYPE
        self.entities = []

    def add_entity(self, entity):
        self.entities.append(entity)

    def update(self, dt):
        for entity in self.entities:
            entity.update(dt)

    def draw(self, surface, camera_offset):
        for entity in self.entities:
            entity.draw(surface, camera_offset)
