# control.py

import math
import pygame

class Controller:
    """Базовый интерфейс контроллера"""
    def update(self, entity, dt):
        raise NotImplementedError("Controller must implement update method")

class KeyboardController(Controller):
    def __init__(self, speed=200):
        self.speed = speed  # пикселей в секунду

    def update(self, entity, dt):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]: entity.y -= self.speed * dt
        if keys[pygame.K_s]: entity.y += self.speed * dt
        if keys[pygame.K_a]: entity.x -= self.speed * dt
        if keys[pygame.K_d]: entity.x += self.speed * dt

class AIAgentController(Controller):
    def __init__(self, world, speed=100):
        self.world = world
        self.speed = speed

    def update(self, entity, dt):
        if closest_food := self._find_closest_food(entity):
            dx = closest_food.x - entity.x
            dy = closest_food.y - entity.y
            dist = math.hypot(dx, dy)   
            if dist > 1e-5:
                # Нормализуем и двигаем
                entity.x += self.speed * dt * dx / dist
                entity.y += self.speed * dt * dy / dist

    def _find_closest_food(self, entity):
        if food_entities := [ e for e in self.world.entities if "food" in e.type ]:
            return min(food_entities, key=lambda e: (e.x - entity.x) ** 2 + (e.y - entity.y) ** 2)
        else:
            return None


class MouseController(Controller):
    def __init__(self):
        self.mouse_pos = (0, 0)

    def update(self, entity, dt):
        self.mouse_pos = pygame.mouse.get_pos()
        entity.x, entity.y = self.mouse_pos  # Перемещаем сущность к позиции мыши
        

# control.py

class RotatingController(Controller):
    def __init__(self, speed=200, angular_speed=180):  # град/сек
        self.speed = speed
        self.angular_speed = angular_speed

    def update(self, entity, dt):
        keys = pygame.key.get_pressed()

        # Поворот
        if keys[pygame.K_q]:
            entity.angle -= self.angular_speed * dt
        if keys[pygame.K_e]:
            entity.angle += self.angular_speed * dt

        # Движение вперёд/назад по направлению
        rad = math.radians(entity.angle)
        dx = math.cos(rad) * self.speed * dt
        dy = math.sin(rad) * self.speed * dt

        if keys[pygame.K_w]:
            entity.x += dx
            entity.y += dy
        if keys[pygame.K_s]:
            entity.x -= dx
            entity.y -= dy
