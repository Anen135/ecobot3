import math
import unittest

import numpy as np

from engine.control import create_controller
from engine.entity import Agent, Food, Obstacle
from engine.game_loop import GameLoop
from engine.nn_control import DQN, NNController, cast_ray
from engine.world import World


class NNControllerTests(unittest.TestCase):
    def make_world(self, world_type="infinite", **config):
        world = World()
        world.type = world_type
        world.width = world.height = 100
        controller = NNController(world, ray_count=4, hidden_size=8, **config)
        agent = Agent(20, 50, controller=controller)
        world.add_entity(agent)
        return world, agent, controller

    def test_rays_ignore_self_and_dead_objects_and_stop_at_nearest_hit(self):
        world, agent, controller = self.make_world()
        food = Food(80, 50)
        obstacle = Obstacle(50, 50, 10, 20)
        world.entities.extend([food, obstacle])
        self.assertEqual(cast_ray(world, agent, 0, 100), (25, 2))
        obstacle.is_alive = False
        self.assertEqual(cast_ray(world, agent, 0, 100), (55, 1))
        agent.angle = 90
        observation = controller.observe(agent).reshape(4, 5)
        self.assertEqual(observation[3, 1], 1)
        self.assertEqual(observation[0, 0], 1)

    def test_walls_and_torus_copies(self):
        world, agent, _ = self.make_world("bounded")
        self.assertEqual(cast_ray(world, agent, 0, 200), (80, 3))
        world.type = "torus"
        world.add_entity(Food(90, 50))
        self.assertEqual(cast_ray(world, agent, math.pi, 250), (25, 1))
        world.entities[-1].x = 390
        self.assertEqual(cast_ray(world, agent, math.pi, 250), (25, 1))

    def test_network_learns_known_terminal_target(self):
        network = DQN(2, 8, 2, np.random.default_rng(7), .01)
        batch = [(np.array([1., 0.]), 0, 2., np.zeros(2), 0.)] * 8
        initial = abs(network.predict(batch[0][0])[0] - 2)
        for _ in range(500):
            network.train(batch)
        self.assertLess(abs(network.predict(batch[0][0])[0] - 2), initial / 10)
        self.assertTrue(all(np.isfinite(weight).all() for weight in network.weights))

    def test_runtime_training_and_simultaneous_motion(self):
        world, agent, controller = self.make_world(batch_size=1, warmup_steps=1, target_sync_steps=1)
        world.add_entity(Food(90, 90))
        controller.state = controller.observe(agent)
        controller.action = controller.ACTIONS.index((1, 1))
        weights = [weight.copy() for weight in controller.network.weights]
        world.update(.1)
        self.assertAlmostEqual(agent.angle, 18)
        self.assertGreater(agent.x, 20)
        self.assertGreater(agent.y, 50)
        self.assertEqual(controller.network.steps, 1)
        self.assertTrue(any(not np.array_equal(a, b) for a, b in zip(weights, controller.network.weights)))
        for a, b in zip(controller.network.weights, controller.network.target):
            np.testing.assert_array_equal(a, b)

    def test_blocked_movement_receives_penalty(self):
        world, agent, controller = self.make_world(speed=100)
        world.entities.extend([Obstacle(35, 50, 10, 20), Food(90, 90)])
        controller.state = controller.observe(agent)
        controller.action = controller.ACTIONS.index((1, 0))
        world.update(.1)
        self.assertEqual(agent.x, 20)
        self.assertAlmostEqual(controller.replay[-1][2], -.105)

    def test_last_food_reward_and_learning_survive_world_reset(self):
        generation = {"enabled": True, "seed": 7, "cell_size": 50,
                      "rules": [{"object": "food", "count": 1, "noise": {"type": "white", "scale": 50}}]}
        for mode in ("regenerate", "restart_same"):
            for preserve_score in (False, True):
                with self.subTest(mode=mode, preserve_score=preserve_score):
                    game = GameLoop({"mode": mode, "preserve_score": preserve_score}, generation,
                                    {"controller": {"name": "nn", "speed": 0, "batch_size": 1, "warmup_steps": 1}})
                    controller = game.agent.controller
                    food = next(e for e in game.world.entities if "food" in e.tags)
                    game.agent.x, game.agent.y = food.x, food.y
                    game.update(.01)
                    self.assertEqual(game.round_number, 1)
                    self.assertIs(game.agent.controller, controller)
                    self.assertIs(controller.world, game.world)
                    self.assertAlmostEqual(controller.replay[-1][2], 9.9995)
                    self.assertEqual(controller.replay[-1][4], 0)
                    self.assertEqual(controller.network.steps, 1)
                    game.agent.x = game.agent.y = -1000
                    game.update(.1)
                    self.assertAlmostEqual(controller.replay[-1][2], -.005)

    def test_empty_world_keeps_decision_interval(self):
        world, _, controller = self.make_world()
        for _ in range(5):
            world.update(.01)
        self.assertEqual(len(controller.replay), 0)

    def test_invalid_settings_and_missing_world(self):
        for config in ({"ray_count": 0}, {"gamma": 2}, {"batch_size": 20000}, {"epsilon_min": 2}, {"ray_length": 0}):
            with self.subTest(config=config), self.assertRaises(ValueError):
                NNController(World(), **config)
        with self.assertRaises(ValueError):
            create_controller("nn")


if __name__ == "__main__":
    unittest.main()
