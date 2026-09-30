# main.py
import pygame
from engine import ui
from engine.settings import (WINDOW_WIDTH, WINDOW_HEIGHT, FULLSCREEN, FPS, BACKGROUND_COLOR, TIMESCALE, AGENT_X, AGENT_Y, AGENT_SIZE, AGENT_COLOR, AGENT_LAYER, AGENT_ANGLE, AGENT_CONTROLLER)
from engine.world import World
from engine.camera import Camera
from engine.entity import load_world_objects, Agent
from engine.control import create_controller


pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.FULLSCREEN if FULLSCREEN else 0)
clock = pygame.time.Clock()

# Инициализируем мир
world = World()

# Загружаем объекты из JSON
entities = load_world_objects("config/world_objects.json")
for e in entities:
    world.add_entity(e)


# Камера создаётся до агента, чтобы передать её контроллеру (например, MouseController
# переводит координаты мыши в мировые с учётом смещения камеры)
camera = Camera(world)

# Создаем агента с параметрами и контроллером из config/agent_config.json
agent = Agent( x=AGENT_X, y=AGENT_Y, size=AGENT_SIZE, color=AGENT_COLOR, layer=AGENT_LAYER, angle=AGENT_ANGLE, controller=create_controller(AGENT_CONTROLLER, world=world, camera=camera), )
world.add_entity(agent)
camera.set_target(agent)

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
