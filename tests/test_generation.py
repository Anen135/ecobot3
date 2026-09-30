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

        config["rules"][0]["count"] = 1
        with self.assertRaisesRegex(ValueError, "requested count=1"):
            ProceduralWorldGenerator(config).generate(world)

    def test_count_selects_highest_noise_values_without_reusing_cells(self):
        world = World()
        world.type = "bounded"
        world.width = world.height = 100
        noise = {"type": "white", "scale": 20}
        config = {
            "seed": 7,
            "cell_size": 20,
            "rules": [
                {"object": "food", "count": 3, "noise": noise},
                {"object": "obstacle", "count": 2, "noise": noise, "params": {"width": 10, "height": 10}},
            ],
        }
        generator = ProceduralWorldGenerator(config)

        entities = generator.generate(world)
        ranked = sorted(
            ((generator._sample(generator.rules[0], x, y), x, y) for y in range(10, 100, 20) for x in range(10, 100, 20)),
            key=lambda item: -item[0],
        )

        self.assertEqual(len(entities), 5)
        self.assertEqual({(entity.x, entity.y) for entity in entities if isinstance(entity, Food)},
                         {(x, y) for _, x, y in ranked[:3]})
        self.assertEqual({(entity.x, entity.y) for entity in entities if isinstance(entity, Obstacle)},
                         {(x, y) for _, x, y in ranked[3:5]})

    def test_invalid_rule_fails_before_world_creation(self):
        with self.assertRaisesRegex(ValueError, "unknown object type"):
            ProceduralWorldGenerator({"rules": [{"object": "missing", "noise": {"type": "value"}}]})
        with self.assertRaisesRegex(ValueError, "unknown noise type"):
            ProceduralWorldGenerator({"rules": [{"object": "food", "noise": {"type": "missing"}}]})
        with self.assertRaisesRegex(TypeError, "count must be an integer"):
            ProceduralWorldGenerator({"rules": [{"object": "food", "noise": {"type": "white"}, "count": True}]})
        with self.assertRaisesRegex(ValueError, "count must be at least 0"):
            ProceduralWorldGenerator({"rules": [{"object": "food", "noise": {"type": "white"}, "count": -1}]})


if __name__ == "__main__":
    unittest.main()
