# ui.py

import pygame
from engine.settings import DEBUG, TIMESCALE

def draw_debug_panel(surface, agent, dt, world, clock):
    if not DEBUG:
        return
    font = pygame.font.SysFont(None, 24)
    lines = [
        f"Agent: ({int(agent.x)}, {int(agent.y)})",
        f"FPS: {int(clock.get_fps())}",
        f"Entities: {len(world.entities)}",
        f"dt: {dt:.4f}",
        f"World type: {world.type}",
        f"Timescale: {TIMESCALE}",
    ]
    line_height = 20
    padding = 10
    panel_height = padding * 2 + line_height * len(lines)
    panel = pygame.Surface((220, panel_height), pygame.SRCALPHA)
    panel.fill((0, 0, 0, 150))

    for i, line in enumerate(lines):
        text = font.render(line, True, (255, 255, 255))
        panel.blit(text, (10, padding + i * line_height))


    surface.blit(panel, (10, 10))

def draw_grid(surface, camera_offset, spacing=100, color=(50, 50, 50)):
    start_x = -camera_offset[0] % spacing
    start_y = -camera_offset[1] % spacing

    for x in range(start_x, surface.get_width(), spacing):
        pygame.draw.line(surface, color, (x, 0), (x, surface.get_height()))
    for y in range(start_y, surface.get_height(), spacing):
        pygame.draw.line(surface, color, (0, y), (surface.get_width(), y))