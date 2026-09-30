# world.py

import random  # noqa: F401
import pygame
from .settings import WORLD_WIDTH, WORLD_HEIGHT, WORLD_TYPE, BORDER_COLOR
from .entity import ENTITY_REGISTRY  # noqa: F401


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
            entity.save_position()  # запоминаем позицию на начало кадра
            entity.update(dt)
            self.apply_world_rules(entity)
        # Коллизии обрабатываем после движения всех сущностей
        self.handle_collisions()

    def handle_collisions(self):
        """Проверяет все пары объектов и вызывает on_collision() с обеих сторон."""
        active = [e for e in self.entities if e.is_alive and not e.skip_collision_check()]
        for i in range(len(active)):
            for j in range(i + 1, len(active)):
                a, b = active[i], active[j]
                if not (a.is_alive and b.is_alive):
                    continue
                if self._entities_collide(a, b):
                    a.on_collision(b, self)
                    if a.is_alive and b.is_alive:
                        b.on_collision(a, self)
        # Удаляем мёртвые сущности (например, съеденную еду)
        self.entities[:] = [e for e in self.entities if e.is_alive]

    def _entities_collide(self, a, b):
        a_rect = a.get_rect()
        b_rect = b.get_rect()
        if self.type != "torus":
            return a_rect.colliderect(b_rect)

        return any(
            a_rect.colliderect(b_rect.move(dx, dy))
            for dx in (-self.width, 0, self.width)
            for dy in (-self.height, 0, self.height)
        )

    def apply_world_rules(self, entity):
        if self.type == "infinite":
            # В бесконечном мире нет ограничений
            return # return вместо pass, чтобы sourcery не ругался на пустой метод
        if self.type == "bounded":
            half_width = getattr(entity, "width", entity.size) / 2
            half_height = getattr(entity, "height", entity.size) / 2
            entity.x = max(half_width, min(entity.x, self.width - half_width))
            entity.y = max(half_height, min(entity.y, self.height - half_height))
        elif self.type == "torus":
            entity.x %= self.width
            entity.y %= self.height

    def draw(self, surface, camera_offset):
        self.entities.sort(key=lambda e: e.layer)  # сортируем по слою
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
            positions.extend((x + dx, y + dy) for dy in [-h, 0, h])
        return positions
