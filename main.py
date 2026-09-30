import pygame
from engine import ui
from engine.settings import (WINDOW_WIDTH, WINDOW_HEIGHT, FULLSCREEN, FPS, BACKGROUND_COLOR, TIMESCALE, AGENT_CONFIG, GENERATION_CONFIG, GAME_LOOP_CONFIG, LOAD_STATIC_OBJECTS)
from engine.game_loop import GameLoop


pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.FULLSCREEN if FULLSCREEN else 0)
clock = pygame.time.Clock()

game = GameLoop(
    GAME_LOOP_CONFIG,
    GENERATION_CONFIG,
    AGENT_CONFIG,
    static_objects_path="config/world_objects.json" if LOAD_STATIC_OBJECTS else None,
)

running = True
while running:
    dt = (clock.tick(FPS) / 1000.0) * TIMESCALE
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False
            
    game.update(dt)
    game.camera.update()
    
    screen.fill(BACKGROUND_COLOR)   
    ui.draw_grid(screen, game.camera.offset)
    game.world.draw(screen, game.camera.offset)
    
    ui.draw_debug_panel(screen, game.agent, dt, game.world, clock)
    
    
    pygame.display.flip()

pygame.quit()
