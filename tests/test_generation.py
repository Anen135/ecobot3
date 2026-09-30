import unittest

from engine.entity import Food, Obstacle
from engine.generation import ProceduralWorldGenerator
from engine.world import World


class GenerationTests(unittest.TestCase):
    def test_noise_types_are_deterministic_and_normalized(self):
        for noise_type in ProceduralWorldGenerator.NOISE_TYPES:
            noise = {"type": noise_type, "scale": 35}
            if noise_type in {"value", "perlin"}:
                noise["octaves"] = 3
            config = {
                "seed": 12,
                "rules": [{"object": "food", "noise": noise, "range": [0, 1]}],
            }
            first = ProceduralWorldGenerator(config)
            second = ProceduralWorldGenerator(config)
            samples = [first._sample(first.rules[0], x, y) for x, y in ((2, 3), (21, 55), (97, 80))]
            self.assertEqual(samples, [second._sample(second.rules[0], x, y) for x, y in ((2, 3), (21, 55), (97, 80))])
            self.assertTrue(all(0 <= value <= 1 for value in samples))

    def test_rules_place_registered_objects_once_per_cell(self):
        world = World()
        world.type = "bounded"
        world.width = world.height = 100
        noise = {"type": "white", "scale": 20}
        config = {
            "seed": 123,
            "cell_size": 20,
            "rules": [
                {"object": "food", "noise": noise, "range": [0, 0.5], "params": {"size": 8}},
                {"object": "obstacle", "noise": noise, "range": [0.5, 1], "params": {"width": 10, "height": 10}},
            ],
        }

        generated = ProceduralWorldGenerator(config).generate(world)
        repeated = ProceduralWorldGenerator(config).generate(world)

        self.assertEqual(len(generated), 25)
        self.assertTrue(any(isinstance(entity, Food) for entity in generated))
        self.assertTrue(any(isinstance(entity, Obstacle) for entity in generated))
        self.assertEqual(
            [(type(entity), entity.x, entity.y) for entity in generated],
            [(type(entity), entity.x, entity.y) for entity in repeated],
        )
        self.assertEqual(world.entities, [])

        changed_seed = ProceduralWorldGenerator(dict(config, seed=124)).generate(world)
        self.assertNotEqual(
            [type(entity) for entity in generated],
            [type(entity) for entity in changed_seed],
        )

    def test_disabled_generation_and_bounded_placement(self):
        world = World()
        world.type = "bounded"
        world.width = world.height = 40
        config = {
            "enabled": False,
            "cell_size": 20,
            "rules": [{"object": "obstacle", "noise": {"type": "white"}, "params": {"width": 50, "height": 50}}],
        }
        self.assertEqual(ProceduralWorldGenerator(config).generate(world), [])

        config["enabled"] = True
        self.assertEqual(ProceduralWorldGenerator(config).generate(world), [])

    def test_invalid_rule_fails_before_world_creation(self):
        with self.assertRaisesRegex(ValueError, "unknown object type"):
            ProceduralWorldGenerator({"rules": [{"object": "missing", "noise": {"type": "value"}}]})
        with self.assertRaisesRegex(ValueError, "unknown noise type"):
            ProceduralWorldGenerator({"rules": [{"object": "food", "noise": {"type": "missing"}}]})


if __name__ == "__main__":
    unittest.main()
