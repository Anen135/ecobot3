# entity.py

import pygame

class Entity:
    def __init__(self, x, y, size=20, color=(255, 255, 255)):
        self.x = x
        self.y = y
        self.size = size
        self.color = color

    def update(self, dt):
        pass  # To be overridden

    def draw(self, surface, camera_offset=(0, 0)):
        rect = pygame.Rect(
            self.x - self.size // 2 - camera_offset[0],
            self.y - self.size // 2 - camera_offset[1],
            self.size,
            self.size
        )
        pygame.draw.rect(surface, self.color, rect)
