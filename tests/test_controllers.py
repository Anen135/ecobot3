import math
import unittest
from collections import defaultdict
from unittest.mock import patch

import pygame

from engine.control import (
    AIAgentController,
    Controller,
    KeyboardController,
    MouseController,
    RotatingController,
    create_controller,
)
from engine.entity import Agent, Food
from engine.world import World


class ControllerTests(unittest.TestCase):
    def test_base_contract_is_abstract_and_all_controllers_have_both_speeds(self):
        with self.assertRaises(TypeError):
            Controller()

        world = World()
        camera = object()
        for name in ("keyboard", "rotate", "mouse", "ai"):
            controller = create_controller(
                {"name": name, "speed": 12, "angular_speed": 34},
                world=world,
                camera=camera,
            )
            self.assertIsInstance(controller, Controller)
            self.assertEqual((controller.speed, controller.angular_speed), (12, 34))

        with self.assertRaises(ValueError):
            KeyboardController(speed=-1)

    def test_forward_and_backward_use_the_same_movement_rule(self):
        agent = Agent(4, 7, angle=30)
        controller = KeyboardController(speed=10)

        controller.move_forward(agent, 2)
        controller.move_backward(agent, 2)

        self.assertAlmostEqual(agent.x, 4)
        self.assertAlmostEqual(agent.y, 7)

    def test_keyboard_moves_along_heading_after_turn(self):
        agent = Agent(0, 0)
        controller = KeyboardController(speed=10, angular_speed=90)
        keys = defaultdict(bool, {pygame.K_a: True, pygame.K_w: True})

        with patch("pygame.key.get_pressed", return_value=keys):
            controller.update(agent, 1)

        self.assertAlmostEqual(agent.angle, 270)
        self.assertAlmostEqual(agent.x, 0)
        self.assertAlmostEqual(agent.y, -10)

    def test_rotate_controller_moves_backward_along_heading(self):
        agent = Agent(0, 0)
        controller = RotatingController(speed=10, angular_speed=90)
        keys = defaultdict(bool, {pygame.K_e: True, pygame.K_s: True})

        with patch("pygame.key.get_pressed", return_value=keys):
            controller.update(agent, 1)

        self.assertAlmostEqual(agent.angle, 90)
        self.assertAlmostEqual(agent.x, 0)
        self.assertAlmostEqual(agent.y, -10)

    def test_ai_moves_while_turning(self):
        world = World()
        world.type = "bounded"
        world.add_entity(Food(0, 100))
        agent = Agent(0, 0)
        controller = AIAgentController(world, speed=10, angular_speed=90)

        controller.update(agent, 0.5)
        self.assertAlmostEqual(agent.angle, 45)
        self.assertAlmostEqual(agent.x, 5 / math.sqrt(2))
        self.assertAlmostEqual(agent.y, 5 / math.sqrt(2))

        distance_after_first_step = math.hypot(agent.x, 100 - agent.y)
        controller.update(agent, 0.5)
        self.assertLess(math.hypot(agent.x, 100 - agent.y), distance_after_first_step)

    def test_mouse_moves_while_turning(self):
        agent = Agent(0, 0)
        controller = MouseController(speed=10, angular_speed=90)

        with patch("pygame.mouse.get_pos", return_value=(0, 100)):
            controller.update(agent, 0.5)
            self.assertAlmostEqual(agent.angle, 45)
            self.assertAlmostEqual(agent.x, 5 / math.sqrt(2))
            self.assertAlmostEqual(agent.y, 5 / math.sqrt(2))

            distance_after_first_step = math.hypot(agent.x, 100 - agent.y)
            controller.update(agent, 1)

        self.assertLess(math.hypot(agent.x, 100 - agent.y), distance_after_first_step)

    def test_target_controller_limits_travel_without_changing_movement_method(self):
        agent = Agent(0, 0)
        controller = MouseController(speed=10)

        with patch("pygame.mouse.get_pos", return_value=(3, 0)):
            controller.update(agent, 1)

        self.assertAlmostEqual(agent.x, 3)
        self.assertAlmostEqual(agent.y, 0)


if __name__ == "__main__":
    unittest.main()
