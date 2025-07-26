# entity.py

import pygame

class Entity:
    def __init__(self, x, y, size=20, color=(255, 255, 255)):
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.is_alive = True  # можно будет "убить" еду

    def update(self, dt):
        pass  # To be overridden

    def draw(self, surface, camera_offset=(0, 0), override_position=None):
        if override_position:
            draw_x, draw_y = override_position
        else:
            draw_x, draw_y = self.x, self.y

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
    def __init__(self, x, y, size=10, color=(255, 0, 0)):
        super().__init__(x, y, size, color)
    
    def update(self, dt):
        pass  # Food doesn't need to update

class Agent(Entity):
    def __init__(self, x, y, size=20, color=(0, 255, 0), controller=None):
        super().__init__(x, y, size, color)
        self.controller = controller

    def update(self, dt):
        if self.controller:
            self.controller.update(self, dt)
