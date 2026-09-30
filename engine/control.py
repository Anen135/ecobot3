# control.py

import math
import pygame

class Controller:
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
            dx, dy = self._displacement(entity, closest_food)
            dist = math.hypot(dx, dy)   
            if dist > 1e-5:
                # Нормализуем и двигаем
                move = min(self.speed * dt, dist)
                entity.x += move * dx / dist
                entity.y += move * dy / dist

    def _displacement(self, entity, target):
        dx = target.x - entity.x
        dy = target.y - entity.y
        if self.world.type == "torus":
            dx = (dx + self.world.width / 2) % self.world.width - self.world.width / 2
            dy = (dy + self.world.height / 2) % self.world.height - self.world.height / 2
        return dx, dy

    def _find_closest_food(self, entity):
        if food_entities := [e for e in self.world.entities if "food" in e.tags]:
            return min(food_entities, key=lambda e: sum(d ** 2 for d in self._displacement(entity, e)))
        else:
            return None


class MouseController(Controller):
    """Агент поворачивается к курсору и движется к нему (как ослик за морковкой)."""
    def __init__(self, speed=200, angular_speed=180, camera=None):
        self.speed = speed  # пикселей в секунду
        self.angular_speed = angular_speed  # град/сек
        self.camera = camera

    def update(self, entity, dt):
        # Экранные координаты мыши -> мировые (с учётом смещения камеры)
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if self.camera is not None:
            mouse_x += self.camera.offset[0]
            mouse_y += self.camera.offset[1]

        dx = mouse_x - entity.x
        dy = mouse_y - entity.y
        dist = math.hypot(dx, dy)
        if dist < 1e-5:
            return  # уже в точке цели

        # Поворачиваем направление (рисуемую "голову") к цели
        target_angle = math.degrees(math.atan2(dy, dx))
        diff = (target_angle - entity.angle + 180.0) % 360.0 - 180.0
        max_turn = self.angular_speed * dt
        entity.angle += max(-max_turn, min(max_turn, diff))

        # Движение к цели (не дальше оставшейся дистанции — не проскакиваем мимо)
        move = min(self.speed * dt, dist)
        entity.x += dx / dist * move
        entity.y += dy / dist * move
        

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

def create_controller(config=None, world=None, camera=None):
    if not config:
        return None
    if isinstance(config, str):
        config = {"name": config}
    name = config.get("name")
    if not name:
        return None

    if name == "keyboard":
        return KeyboardController(speed=config.get("speed", 200))

    if name == "rotate":
        return RotatingController(
            speed=config.get("speed", 200),
            angular_speed=config.get("angular_speed", 180),
        )

    if name == "mouse":
        if camera is None:
            raise ValueError("Controller 'mouse' requires a camera reference")
        return MouseController(
            speed=config.get("speed", 200),
            angular_speed=config.get("angular_speed", 180),
            camera=camera,
        )

    if name == "ai":
        if world is None:
            raise ValueError("Controller 'ai' requires a world reference")
        return AIAgentController(world, speed=config.get("speed", 100))

    raise ValueError(f"Unknown controller '{name}'")
