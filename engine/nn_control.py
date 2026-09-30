import math
from collections import deque

import numpy as np
import pygame

from .control import Controller


def ray_box(x, y, dx, dy, rect, limit):
    near, far = 0.0, limit
    for origin, direction, low, high in (
        (x, dx, rect.left, rect.right), (y, dy, rect.top, rect.bottom)
    ):
        if abs(direction) < 1e-12:
            if origin < low or origin > high:
                return None
        else:
            a, b = (low - origin) / direction, (high - origin) / direction
            near, far = max(near, min(a, b)), min(far, max(a, b))
            if near > far:
                return None
    return near


def cast_ray(world, agent, angle, limit):
    dx, dy = math.cos(angle), math.sin(angle)
    distance, kind = limit, 0
    if world.type == "bounded":
        for origin, direction, edge in ((agent.x, dx, world.width), (agent.y, dy, world.height)):
            if abs(direction) > 1e-12:
                hit = ((edge if direction > 0 else 0) - origin) / direction
                if 0 <= hit <= distance:
                    distance, kind = hit, 3
    for target in world.entities:
        if target is agent or not target.is_alive:
            continue
        rect = target.get_rect()
        xs, ys = (0,), (0,)
        if world.type == "torus":
            xs = range(math.ceil((agent.x - limit - rect.right) / world.width),
                       math.floor((agent.x + limit - rect.left) / world.width) + 1)
            ys = range(math.ceil((agent.y - limit - rect.bottom) / world.height),
                       math.floor((agent.y + limit - rect.top) / world.height) + 1)
        for ix in xs:
            for iy in ys:
                shifted = rect.move(ix * world.width, iy * world.height)
                hit = ray_box(agent.x, agent.y, dx, dy, shifted, distance)
                if hit is not None and hit <= distance:
                    distance = hit
                    kind = 2 if target.blocks_movement else (1 if "food" in target.tags else 4)
    return distance, kind


class DQN:
    def __init__(self, inputs, hidden, actions, rng, learning_rate):
        self.rng = rng
        self.learning_rate = learning_rate
        self.weights = [rng.normal(0, math.sqrt(2 / inputs), (inputs, hidden)),
                        np.zeros(hidden), rng.normal(0, math.sqrt(2 / hidden), (hidden, actions)),
                        np.zeros(actions)]
        self.target = [w.copy() for w in self.weights]
        self.m = [np.zeros_like(w) for w in self.weights]
        self.v = [np.zeros_like(w) for w in self.weights]
        self.steps = 0
        self.loss = 0.0

    def predict(self, states, target=False):
        w, b, out, bias = self.target if target else self.weights
        return np.maximum(0, states @ w + b) @ out + bias

    def train(self, batch):
        states, actions, rewards, next_states, discounts = map(np.asarray, zip(*batch))
        w, b, out, _ = self.weights
        hidden = np.maximum(0, states @ w + b)
        predictions = self.predict(states)
        next_actions = self.predict(next_states).argmax(axis=1)
        targets = rewards + discounts * self.predict(next_states, target=True)[np.arange(len(batch)), next_actions]
        errors = predictions[np.arange(len(batch)), actions] - targets
        absolute = np.abs(errors)
        self.loss = float(np.mean(np.where(absolute <= 1, errors ** 2 / 2, absolute - .5)))
        delta = np.zeros_like(predictions)
        delta[np.arange(len(batch)), actions] = np.clip(errors, -1, 1) / len(batch)
        back = (delta @ out.T) * (hidden > 0)
        gradients = [states.T @ back, back.sum(axis=0), hidden.T @ delta, delta.sum(axis=0)]
        self.steps += 1
        for weight, grad, m, v in zip(self.weights, gradients, self.m, self.v):
            np.clip(grad, -5, 5, out=grad)
            m *= .9
            m += .1 * grad
            v *= .999
            v += .001 * grad ** 2
            weight -= self.learning_rate * (m / (1 - .9 ** self.steps)) / (np.sqrt(v / (1 - .999 ** self.steps)) + 1e-8)


class NNController(Controller):
    persist_across_worlds = True
    ACTIONS = tuple((move, turn) for move in (-1, 0, 1) for turn in (-1, 0, 1))

    def __init__(self, world, speed=200, angular_speed=180, **config):
        super().__init__(speed, angular_speed)
        defaults = {
            "ray_count": 24, "ray_length": 350.0, "hidden_size": 64, "decision_interval": .1,
            "learning_rate": .001, "gamma": .99, "epsilon_start": 1.0, "epsilon_min": .05,
            "epsilon_decay": .9995, "replay_capacity": 10000, "batch_size": 32,
            "warmup_steps": 128, "target_sync_steps": 200, "food_reward": 10.0,
            "time_penalty": .05, "blocked_penalty": 1.0, "seed": 42, "draw_rays": True,
        }
        unknown = config.keys() - defaults.keys()
        if unknown:
            raise ValueError(f"Unknown NN settings: {sorted(unknown)}")
        defaults.update(config)
        integers = {"ray_count", "hidden_size", "replay_capacity", "batch_size", "warmup_steps", "target_sync_steps"}
        for key, value in defaults.items():
            if key == "draw_rays":
                if not isinstance(value, bool):
                    raise TypeError("draw_rays must be boolean")
            elif key == "seed":
                if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                    raise ValueError("seed must be a non-negative integer")
            elif isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
                raise ValueError(f"Invalid NN setting: {key}")
            elif key in integers and (not isinstance(value, int) or value < 1):
                raise ValueError(f"{key} must be a positive integer")
            setattr(self, key, value)
        if min(self.ray_length, self.decision_interval, self.learning_rate) <= 0:
            raise ValueError("ray_length, decision_interval and learning_rate must be positive")
        if not (0 <= self.epsilon_min <= self.epsilon_start <= 1 and 0 < self.epsilon_decay <= 1 and 0 <= self.gamma <= 1):
            raise ValueError("Invalid exploration or discount settings")
        if self.replay_capacity < max(self.batch_size, self.warmup_steps):
            raise ValueError("replay_capacity must cover batch_size and warmup_steps")
        self.world = world
        self.rng = np.random.default_rng(self.seed)
        self.network = DQN(self.ray_count * 5, self.hidden_size, len(self.ACTIONS), self.rng, self.learning_rate)
        self.replay = deque(maxlen=self.replay_capacity)
        self.epsilon = self.epsilon_start
        self.state = None
        self.elapsed = 0.0
        self.reward = 0.0
        self.last_reward = 0.0
        self.rays = []

    def observe(self, entity):
        state = np.zeros((self.ray_count, 5))
        self.rays = []
        for i in range(self.ray_count):
            angle = math.radians(entity.angle) + i * math.tau / self.ray_count
            distance, kind = cast_ray(self.world, entity, angle, self.ray_length)
            state[i, 0] = distance / self.ray_length
            if kind:
                state[i, kind] = 1
            self.rays.append((angle, distance, kind))
        return state.ravel()

    def update(self, entity, dt):
        if not math.isfinite(dt) or dt < 0:
            raise ValueError("dt must be finite and non-negative")
        if self.state is None:
            self.state = self.observe(entity)
            self.action = int(self.rng.integers(len(self.ACTIONS))) if self.rng.random() < self.epsilon else int(self.network.predict(self.state).argmax())
        self.before_score = entity.score
        move, turn = self.ACTIONS[self.action]
        if turn:
            (self.turn_right if turn > 0 else self.turn_left)(entity, dt)
        if move:
            (self.move_forward if move > 0 else self.move_backward)(entity, dt)
        self.expected_position = (entity.x, entity.y)
        self.elapsed += dt

    def after_step(self, entity, dt):
        if self.state is None:
            return
        self.reward += (entity.score - self.before_score) * self.food_reward - self.time_penalty * dt
        ex, ey = self.expected_position
        if self.world.type == "torus":
            ex, ey = ex % self.world.width, ey % self.world.height
        if math.hypot(entity.x - ex, entity.y - ey) > 1e-6:
            self.reward -= self.blocked_penalty * dt
        terminal = not any(e.is_alive and "food" in e.tags for e in self.world.entities)
        if self.elapsed < self.decision_interval and not (terminal and entity.score > self.before_score):
            return
        next_state = self.observe(entity)
        if self.elapsed > 0 or self.reward != 0:
            discount = 0.0 if terminal else self.gamma ** (self.elapsed / self.decision_interval)
            self.replay.append((self.state, self.action, self.reward, next_state, discount))
            if len(self.replay) >= max(self.batch_size, self.warmup_steps):
                indices = self.rng.choice(len(self.replay), self.batch_size, replace=False)
                self.network.train([self.replay[int(i)] for i in indices])
                self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
                if self.network.steps % self.target_sync_steps == 0:
                    self.network.target = [w.copy() for w in self.network.weights]
        self.last_reward = self.reward
        self.state, self.reward, self.elapsed = None, 0.0, 0.0

    def reset_world(self, world):
        self.world = world
        self.state, self.reward, self.elapsed = None, 0.0, 0.0
        self.rays = []

    def draw(self, surface, entity, camera_offset, override_position):
        if not self.draw_rays:
            return
        x, y = override_position or (entity.x, entity.y)
        start = (x - camera_offset[0], y - camera_offset[1])
        colors = ((45, 55, 65), (40, 210, 80), (220, 70, 50), (220, 150, 40), (80, 130, 220))
        for angle, distance, kind in self.rays:
            end = (start[0] + math.cos(angle) * distance, start[1] + math.sin(angle) * distance)
            pygame.draw.line(surface, colors[kind], start, end)
