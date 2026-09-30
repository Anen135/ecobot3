import unittest

from engine.camera import Camera
from engine.control import AIAgentController
from engine.entity import Agent, Food, Obstacle
from engine.world import World


class WorldBehaviorTests(unittest.TestCase):
    def test_torus_collision_crosses_both_edges(self):
        world = World()
        world.type = "torus"
        food = Food(2, 2)
        agent = Agent(world.width - 2, world.height - 2)
        world.add_entity(food)
        world.add_entity(agent)

        world.update(0)

        self.assertEqual(agent.score, 1)
        self.assertNotIn(food, world.entities)

    def test_bounded_world_does_not_wrap_collisions(self):
        world = World()
        world.type = "bounded"
        food = Food(2, 100)
        agent = Agent(world.width - 10, 100)
        world.add_entity(food)
        world.add_entity(agent)

        world.update(0)

        self.assertEqual(agent.score, 0)
        self.assertIn(food, world.entities)

    def test_ai_selects_nearest_food_across_torus_edge(self):
        world = World()
        world.type = "torus"
        agent = Agent(world.width - 5, world.height - 5)
        near_food = Food(2, 2)
        far_food = Food(world.width - 100, world.height - 100)
        world.add_entity(far_food)
        world.add_entity(near_food)
        controller = AIAgentController(world, speed=5)

        self.assertIs(controller._find_closest_food(agent), near_food)
        controller.update(agent, 1)

        self.assertGreater(agent.x, world.width - 5)
        self.assertGreater(agent.y, world.height - 5)

    def test_follow_food_uses_tag_independent_of_color(self):
        world = World()
        world.type = "torus"
        food = Food(600, 400, color=[12, 30, 40])
        world.add_entity(food)
        camera = Camera(world, target=Agent(100, 100))
        camera.set_mode("follow_food")

        camera.update()

        self.assertIs(camera._find_nearest_food(), food)
        self.assertEqual(camera.offset, [200, 100])

    def test_bounded_obstacle_stays_inside_world(self):
        world = World()
        world.type = "bounded"
        obstacle = Obstacle(world.width - 20, world.height - 10, 100, 50)

        world.apply_world_rules(obstacle)

        self.assertLessEqual(obstacle.get_rect().right, world.width)
        self.assertLessEqual(obstacle.get_rect().bottom, world.height)


if __name__ == "__main__":
    unittest.main()
