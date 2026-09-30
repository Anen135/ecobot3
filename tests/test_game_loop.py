import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from engine.game_loop import GameLoop


AGENT_CONFIG = {
    "x": 100,
    "y": 200,
    "angle": 30,
    "controller": {"name": "mouse", "speed": 20},
}
GENERATION_CONFIG = {
    "enabled": True,
    "seed": 7,
    "cell_size": 50,
    "rules": [{"object": "food", "count": 1, "noise": {"type": "white", "scale": 50}}],
}


def food_positions(game):
    return [(entity.x, entity.y) for entity in game.world.entities if "food" in entity.tags]


def eat_last_food(game):
    food = next(entity for entity in game.world.entities if "food" in entity.tags)
    game.agent.x, game.agent.y = food.x, food.y
    game.update(0)
    return food.x, food.y


class GameLoopTests(unittest.TestCase):
    def setUp(self):
        mouse_patch = patch("pygame.mouse.get_pos", return_value=(0, 0))
        mouse_patch.start()
        self.addCleanup(mouse_patch.stop)

    def test_none_keeps_finished_world(self):
        game = GameLoop({"mode": "none"}, GENERATION_CONFIG, AGENT_CONFIG)
        original_world = game.world

        eat_last_food(game)
        game.update(0)

        self.assertIs(game.world, original_world)
        self.assertEqual(food_positions(game), [])
        self.assertEqual(game.agent.score, 1)
        self.assertEqual(game.round_number, 0)

    def test_restart_same_restores_layout_position_and_score(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "objects.json"
            path.write_text(json.dumps({"objects": [
                {"type": "food", "x": 300, "y": 400},
                {"type": "obstacle", "x": 600, "y": 600, "width": 30, "height": 30},
            ]}), encoding="utf-8")
            game = GameLoop(
                {"mode": "restart_same", "reset_agent_position": True, "preserve_score": False},
                {"enabled": False},
                AGENT_CONFIG,
                static_objects_path=path,
            )
            original_world = game.world
            original_layout = [(type(entity), entity.x, entity.y) for entity in game.world.entities[:-1]]
            path.write_text(json.dumps({"objects": []}), encoding="utf-8")

            eat_last_food(game)

        self.assertIsNot(game.world, original_world)
        self.assertEqual([(type(entity), entity.x, entity.y) for entity in game.world.entities[:-1]], original_layout)
        self.assertEqual((game.agent.x, game.agent.y, game.agent.angle), (100, 200, 30))
        self.assertEqual(game.agent.score, 0)
        self.assertEqual(game.round_number, 1)
        self.assertIs(game.camera.world, game.world)
        self.assertIs(game.camera.target, game.agent)
        self.assertIs(game.agent.controller.camera, game.camera)

    def test_regenerate_changes_layout_and_keeps_agent_state(self):
        game = GameLoop(
            {"mode": "regenerate", "reset_agent_position": False, "preserve_score": True},
            GENERATION_CONFIG,
            AGENT_CONFIG,
        )
        original_world = game.world
        original_layout = food_positions(game)

        consumed_at = eat_last_food(game)

        self.assertIsNot(game.world, original_world)
        self.assertNotEqual(food_positions(game), original_layout)
        self.assertEqual((game.agent.x, game.agent.y), consumed_at)
        self.assertEqual(game.agent.score, 1)
        self.assertEqual(game.round_number, 1)
        self.assertIs(game.agent.controller.camera, game.camera)

    def test_same_layout_waits_for_agent_to_leave_respawned_food(self):
        game = GameLoop(
            {"mode": "restart_same", "reset_agent_position": False, "preserve_score": True},
            GENERATION_CONFIG,
            AGENT_CONFIG,
        )
        food_position = eat_last_food(game)

        game.update(0)
        self.assertEqual((game.round_number, game.agent.score), (1, 1))

        game.agent.x += 100
        game.update(0)
        self.assertEqual(game.round_number, 1)

        game.agent.x, game.agent.y = food_position
        game.update(0)
        self.assertEqual((game.round_number, game.agent.score), (2, 2))

    def test_reset_at_food_spawn_does_not_restart_every_frame(self):
        sample = GameLoop({"mode": "none"}, GENERATION_CONFIG, AGENT_CONFIG)
        food_x, food_y = food_positions(sample)[0]
        agent_config = dict(AGENT_CONFIG, x=food_x, y=food_y)
        game = GameLoop(
            {"mode": "restart_same", "reset_agent_position": True, "preserve_score": True},
            GENERATION_CONFIG,
            agent_config,
        )

        game.update(0)
        game.update(0)

        self.assertEqual((game.round_number, game.agent.score), (1, 1))

    def test_empty_world_does_not_restart_every_frame(self):
        game = GameLoop({"mode": "regenerate"}, {"enabled": False}, AGENT_CONFIG)
        original_world = game.world

        game.update(0)
        game.update(0)

        self.assertIs(game.world, original_world)
        self.assertEqual(game.round_number, 0)

    def test_unknown_mode_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Unknown game loop mode"):
            GameLoop({"mode": "unknown"}, GENERATION_CONFIG, AGENT_CONFIG)


if __name__ == "__main__":
    unittest.main()
