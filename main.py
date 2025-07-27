# main.py
# noqa: E701
import pygame
import random
import engine.ui as ui
from engine.settings import WINDOW_WIDTH, WINDOW_HEIGHT, FULLSCREEN, FPS, BACKGROUND_COLOR, WORLD_WIDTH, WORLD_HEIGHT, TIMESCALE
from engine.world import World
from engine.camera import Camera
from engine.entity import load_world_objects
from engine.control import KeyboardController, MouseController, AIAgentController, RotatingController  # noqa: F401


pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.FULLSCREEN if FULLSCREEN else 0)
clock = pygame.time.Clock()

# Инициализируем мир
world = World()

# Загружаем объекты из JSON
entities = load_world_objects("config/world_objects.json")
for e in entities:
    world.add_entity(e)


# Камера может навести на первого агента
agent = next((e for e in world.entities if hasattr(e, "id") and e.id == "agent_1"), None)
camera = Camera(world, target=agent)

running = True
while running:
    dt = (clock.tick(FPS) / 1000.0) * TIMESCALE  # delta time в секундах
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False
            
    world.update(dt)
    camera.update()
    
    screen.fill(BACKGROUND_COLOR)   
    ui.draw_grid(screen, camera.offset)
    world.draw(screen, camera.offset)
    
    # Отладочная информация
    ui.draw_debug_panel(screen, agent, dt, world, clock)
    
    
    pygame.display.flip()

pygame.quit()
