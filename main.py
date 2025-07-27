# main.py
import pygame
import random # noqa: F401
import engine.ui as ui
from engine.settings import WINDOW_WIDTH, WINDOW_HEIGHT, FULLSCREEN, FPS, BACKGROUND_COLOR, TIMESCALE
from engine.world import World
from engine.camera import Camera
from engine.entity import load_world_objects, Agent
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


agent = Agent(x=100, y=200, controller=RotatingController())  # Создаем агента с начальной позицией и углом
world.add_entity(agent)
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
