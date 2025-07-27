# entity.py

import pygame
import math
import json

class Entity:
    def __init__(self, x, y, layer, size=20, color=(255, 255, 255), tags=None):
        self.x = x
        self.y = y
        self.layer = layer # -1 - background, 0 - objects, 1+ - effects
        self.size = size
        self.color = color
        self.tags = set(tags or [])
        self.is_alive = True

    def update(self, dt):
        pass  # To be overridden

    def draw(self, surface, camera_offset=(0, 0), override_position=None):
        draw_x, draw_y = override_position or (self.x, self.y)
        rect = pygame.Rect(
            draw_x - self.size // 2 - camera_offset[0],
            draw_y - self.size // 2 - camera_offset[1],
            self.size,
            self.size
        )
        pygame.draw.rect(surface, self.color, rect)
    
    def get_rect(self):
        return pygame.Rect(
            self.x - self.size // 2,
            self.y - self.size // 2,
            self.size,
            self.size
        )
    
class Food(Entity):
    def __init__(self, x, y, size=10, color=(255, 0, 0), layer=0):
        super().__init__(x, y, layer, size, color, tags={"food"})
    
    def update(self, dt):
        pass  # Food doesn't need to update

class Obstacle(Entity):
    def __init__(self, x, y, width, height, color=(100, 100, 100), layer=0):
        # Заменяем size на width/height, но всё ещё передаём size как среднее значение для совместимости
        size = (width + height) // 2
        super().__init__(x, y, layer, size, color, tags={"obstacle"})
        self.width = width
        self.height = height

    def update(self, dt):
        pass  # Obstacles are static

    def draw(self, surface, camera_offset=(0, 0), override_position=None):
        draw_x, draw_y = override_position or (self.x, self.y)
        rect = pygame.Rect(
            draw_x - self.width // 2 - camera_offset[0],
            draw_y - self.height // 2 - camera_offset[1],
            self.width,
            self.height
        )
        pygame.draw.rect(surface, self.color, rect)

    def get_rect(self):
        return pygame.Rect(
            self.x - self.width // 2,
            self.y - self.height // 2,
            self.width,
            self.height
        )


class Agent(Entity):
    def __init__(self, x, y, size=20, color=(0, 255, 0), layer=0, controller=None, angle=0):
        super().__init__(x, y, layer, size, color, tags={"agent"})
        self.controller = controller
        self.angle = angle  # угол в градусах, 0 = вправо

    def update(self, dt):
        
        if self.controller:
            self.controller.update(self, dt)

    def draw(self, surface, camera_offset=(0, 0)):
        super().draw(surface, camera_offset)

        # Отрисуем направление
        cx = self.x - camera_offset[0]
        cy = self.y - camera_offset[1]
        length = self.size * 1.5

        # Угол → радианы
        rad = math.radians(self.angle)
        dx = math.cos(rad) * length
        dy = math.sin(rad) * length

        end_pos = (cx + dx, cy + dy)
        pygame.draw.line(surface, (255, 255, 0), (cx, cy), end_pos, 2)

ENTITY_REGISTRY = {
    "agent": Agent,
    "food": Food,
    "obstacle": Obstacle
}

def load_world_objects(filepath):
    with open(filepath, "r") as f:
        data = json.load(f)

    objects = []
    for obj in data.get("objects", []):
        obj_type = obj.get("type")
        if obj_type not in ENTITY_REGISTRY:
            print(f"[!] Unknown object type '{obj_type}', skipped.")
            continue

        cls = ENTITY_REGISTRY[obj_type]
        params = obj.copy()
        params.pop("type", None)

        try:
            entity = cls(**params)
            objects.append(entity)
        except Exception as e:
            print(f"[!] Failed to create {obj_type}: {e}")

    return objects