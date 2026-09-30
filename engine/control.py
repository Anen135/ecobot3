import math
from abc import ABC, abstractmethod

import pygame


class Controller(ABC):
    def __init__(self, speed=200, angular_speed=180):
        for name, value in (("speed", speed), ("angular_speed", angular_speed)):
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
                raise ValueError(f"{name} must be a finite non-negative number")
        self.speed = speed
        self.angular_speed = angular_speed

    @abstractmethod
    def update(self, entity, dt):
        pass

    def _move(self, entity, distance):
        radians = math.radians(entity.angle)
        entity.x += math.cos(radians) * distance
        entity.y += math.sin(radians) * distance

    def move_forward(self, entity, dt):
        self._move(entity, self.speed * dt)

    def move_backward(self, entity, dt):
        self._move(entity, -self.speed * dt)

    def turn_left(self, entity, dt):
        entity.angle = (entity.angle - self.angular_speed * dt) % 360

    def turn_right(self, entity, dt):
        entity.angle = (entity.angle + self.angular_speed * dt) % 360

    def _move_towards(self, entity, dx, dy, dt):
        distance = math.hypot(dx, dy)
        if distance <= 1e-5:
            return

        target_angle = math.degrees(math.atan2(dy, dx))
        angle_diff = (target_angle - entity.angle + 180) % 360 - 180
        if abs(angle_diff) > 1e-9 and self.angular_speed > 0:
            turn_time = min(dt, abs(angle_diff) / self.angular_speed)
            if angle_diff < 0:
                self.turn_left(entity, turn_time)
            else:
                self.turn_right(entity, turn_time)
            if turn_time >= abs(angle_diff) / self.angular_speed:
                entity.angle = target_angle % 360

        if dt > 0 and self.speed > 0:
            radians = math.radians(entity.angle)
            forward_distance = dx * math.cos(radians) + dy * math.sin(radians)
            if forward_distance > 0:
                self.move_forward(entity, min(dt, forward_distance / self.speed))

    def _update_from_keys(self, entity, dt, keys, left_key, right_key):
        if keys[left_key]:
            self.turn_left(entity, dt)
        if keys[right_key]:
            self.turn_right(entity, dt)
        if keys[pygame.K_w]:
            self.move_forward(entity, dt)
        if keys[pygame.K_s]:
            self.move_backward(entity, dt)


class KeyboardController(Controller):
    def update(self, entity, dt):
        self._update_from_keys(entity, dt, pygame.key.get_pressed(), pygame.K_a, pygame.K_d)


class RotatingController(Controller):
    def update(self, entity, dt):
        self._update_from_keys(entity, dt, pygame.key.get_pressed(), pygame.K_q, pygame.K_e)


class AIAgentController(Controller):
    def __init__(self, world, speed=100, angular_speed=180):
        super().__init__(speed, angular_speed)
        self.world = world

    def update(self, entity, dt):
        if closest_food := self._find_closest_food(entity):
            self._move_towards(entity, *self._displacement(entity, closest_food), dt)

    def _displacement(self, entity, target):
        dx = target.x - entity.x
        dy = target.y - entity.y
        if self.world.type == "torus":
            dx = (dx + self.world.width / 2) % self.world.width - self.world.width / 2
            dy = (dy + self.world.height / 2) % self.world.height - self.world.height / 2
        return dx, dy

    def _find_closest_food(self, entity):
        foods = (e for e in self.world.entities if e.is_alive and "food" in e.tags)
        return min(foods, key=lambda food: sum(d * d for d in self._displacement(entity, food)), default=None)


class MouseController(Controller):
    def __init__(self, speed=200, angular_speed=180, camera=None):
        super().__init__(speed, angular_speed)
        self.camera = camera

    def update(self, entity, dt):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if self.camera is not None:
            mouse_x += self.camera.offset[0]
            mouse_y += self.camera.offset[1]
        self._move_towards(entity, mouse_x - entity.x, mouse_y - entity.y, dt)


def create_controller(config=None, world=None, camera=None):
    if not config:
        return None
    if isinstance(config, str):
        config = {"name": config}
    name = config.get("name")
    if not name:
        return None

    if name == "keyboard":
        return KeyboardController(
            speed=config.get("speed", 200),
            angular_speed=config.get("angular_speed", 180),
        )

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
        return AIAgentController(
            world,
            speed=config.get("speed", 100),
            angular_speed=config.get("angular_speed", 180),
        )

    raise ValueError(f"Unknown controller '{name}'")
