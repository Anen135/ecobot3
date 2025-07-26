# world.py

import random  # noqa: F401
import pygame
from .settings import WORLD_WIDTH, WORLD_HEIGHT, WORLD_TYPE, BORDER_COLOR
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
            self.apply_world_rules(entity)

    def apply_world_rules(self, entity):
        if self.type == "bounded":
            half = entity.size / 2
            entity.x = max(half, min(entity.x, self.width - half))
            entity.y = max(half, min(entity.y, self.height - half))
        elif self.type == "torus":
            entity.x %= self.width
            entity.y %= self.height
        elif self.type == "infinite":
            pass

    def draw(self, surface, camera_offset):
        if self.type == "torus":
            # TORUS: отрисовка с дубликатами по краям
            for entity in self.entities:
                positions = self.get_wrapped_positions(entity)
                for pos in positions:
                    entity.draw(surface, camera_offset, override_position=pos)
        else:
            # BOUNDED и INFINITE — обычная отрисовка
            for entity in self.entities:
                entity.draw(surface, camera_offset)

        # Отрисовка рамки мира — только для bounded
        if self.type == "bounded":
            rect = pygame.Rect(
                -camera_offset[0],
                -camera_offset[1],
                self.width,
                self.height
            )
            pygame.draw.rect(surface, BORDER_COLOR, rect, width=2)


    def get_wrapped_positions(self, entity):
        """Возвращает список координат, где нужно отрисовать entity"""
        positions = []
        x, y = entity.x, entity.y
        w, h = self.width, self.height

        # основные позиции (центр + по краям)
        for dx in [-w, 0, w]:
            for dy in [-h, 0, h]:
                positions.append((x + dx, y + dy))
        return positions
