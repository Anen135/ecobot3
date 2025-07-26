# main.py
# noqa: E701
import pygame
import random
from engine.settings import WINDOW_WIDTH, WINDOW_HEIGHT, FULLSCREEN, FPS, BACKGROUND_COLOR, WORLD_WIDTH, WORLD_HEIGHT
from engine.world import World
from engine.camera import Camera
from engine.entity import Entity

pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.FULLSCREEN if FULLSCREEN else 0)
clock = pygame.time.Clock()

world = World()
agent = Entity(100, 100, size=20, color=(0, 255, 0))
world.add_entity(agent)

# Добавим еду

for _ in range(10):
    x, y = random.randint(0, WORLD_WIDTH), random.randint(0, WORLD_HEIGHT)
    food = Entity(x, y, size=10, color=(255, 0, 0))
    world.add_entity(food)

camera = Camera(world, target=agent)

running = True
while running:
    dt = clock.tick(FPS) / 1000.0  # delta time в секундах
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False

    keys = pygame.key.get_pressed()
    speed = 200  # пикселей в секунду
    if keys[pygame.K_w]: agent.y -= speed * dt  
    if keys[pygame.K_s]: agent.y += speed * dt
    if keys[pygame.K_a]: agent.x -= speed * dt
    if keys[pygame.K_d]: agent.x += speed * dt

    world.update(dt)
    camera.update()

    screen.fill(BACKGROUND_COLOR)
    world.draw(screen, camera.offset)

    # Отладочная информация
    font = pygame.font.SysFont(None, 24)
    debug_text = f"Agent: ({int(agent.x)}, {int(agent.y)}) | dt: {dt:.4f}"
    screen.blit(font.render(debug_text, True, (255, 255, 255)), (10, 10))

    pygame.display.flip()

pygame.quit()
