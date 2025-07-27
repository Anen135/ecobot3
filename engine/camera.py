# camera.py

from .settings import WINDOW_WIDTH, WINDOW_HEIGHT, CAMERA_MODE

class Camera:
    def __init__(self, world, target=None, fixed_pos=(0, 0)):
        self.world = world
        self.target = target
        self.offset = [0, 0]
        self.mode = CAMERA_MODE
        self.fixed_pos = fixed_pos  # для fixed-режима

    def set_mode(self, mode):
        self.mode = mode

    def set_target(self, entity):
        self.target = entity

    def update(self):
        if self.mode == "fixed":
            self.offset = list(self.fixed_pos)
            return
        
        target = None
        if self.mode == "follow_agent" and self.target:
            target = self.target
        elif self.mode == "follow_food":
            target = self._find_nearest_food()
        if not target:
            return
        
        self.offset[0] = int(target.x - WINDOW_WIDTH // 2)
        self.offset[1] = int(target.y - WINDOW_HEIGHT // 2)
        if self.world.type == "bounded":
            self.offset[0] = max(0, min(self.offset[0], self.world.width - WINDOW_WIDTH))
            self.offset[1] = max(0, min(self.offset[1], self.world.height - WINDOW_HEIGHT))


    def _find_nearest_food(self):
        foods = [e for e in self.world.entities if e.color == (255, 0, 0)]  # красные — еда
        if not foods or not self.target: return None
        foods.sort(key=lambda f: (f.x - self.target.x) ** 2 + (f.y - self.target.y) ** 2)
        return foods[0] if foods else None
