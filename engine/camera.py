# camera.py

from .settings import WINDOW_WIDTH, WINDOW_HEIGHT

class Camera:
    def __init__(self, world, target=None):
        self.world = world
        self.target = target
        self.offset = [0, 0]

    def set_target(self, target):
        self.target = target

    def update(self):
        if not self.target:
            return
        self.offset[0] = int(self.target.x - WINDOW_WIDTH // 2)
        self.offset[1] = int(self.target.y - WINDOW_HEIGHT // 2)

        # Clamp if world is bounded
        if self.world.type == "bounded":
            self.offset[0] = max(0, min(self.offset[0], self.world.width - WINDOW_WIDTH))
            self.offset[1] = max(0, min(self.offset[1], self.world.height - WINDOW_HEIGHT))
