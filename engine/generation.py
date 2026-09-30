import math

from .entity import ENTITY_REGISTRY


class ProceduralWorldGenerator:
    NOISE_TYPES = frozenset({"white", "value", "perlin", "worley"})

    def __init__(self, config, registry=None):
        if not isinstance(config, dict):
            raise TypeError("Generation config must be an object")
        self.enabled = config.get("enabled", True)
        if not isinstance(self.enabled, bool):
            raise TypeError("enabled must be a boolean")
        self.seed = self._integer(config.get("seed", 0), "seed")
        self.cell_size = self._integer(config.get("cell_size", 50), "cell_size", minimum=1)
        self.registry = ENTITY_REGISTRY if registry is None else registry

        rules = config.get("rules", [])
        if not isinstance(rules, list):
            raise TypeError("rules must be an array")
        self.rules = [self._parse_rule(rule, index) for index, rule in enumerate(rules)]

    @staticmethod
    def _number(value, name, minimum=None):
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            raise ValueError(f"{name} must be a finite number")
        if minimum is not None and value < minimum:
            raise ValueError(f"{name} must be at least {minimum}")
        return value

    @staticmethod
    def _integer(value, name, minimum=None):
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError(f"{name} must be an integer")
        if minimum is not None and value < minimum:
            raise ValueError(f"{name} must be at least {minimum}")
        return value

    def _parse_rule(self, rule, index):
        if not isinstance(rule, dict):
            raise TypeError(f"Rule {index} must be an object")

        object_type = rule.get("object")
        if not isinstance(object_type, str) or object_type not in self.registry:
            raise ValueError(f"Rule {index} has unknown object type: {object_type!r}")
        params = rule.get("params", {})
        if not isinstance(params, dict) or "x" in params or "y" in params:
            raise ValueError(f"Rule {index} params must be an object without x or y")
        count = rule.get("count")
        if count is not None:
            count = self._integer(count, f"Rule {index} count", minimum=0)

        value_range = rule.get("range", [0, 1])
        if not isinstance(value_range, list) or len(value_range) != 2:
            raise ValueError(f"Rule {index} range must contain two numbers")
        low = self._number(value_range[0], f"Rule {index} range minimum")
        high = self._number(value_range[1], f"Rule {index} range maximum")
        if not 0 <= low <= high <= 1:
            raise ValueError(f"Rule {index} range must be within [0, 1]")

        noise = rule.get("noise")
        if not isinstance(noise, dict):
            raise TypeError(f"Rule {index} noise must be an object")
        noise_type = noise.get("type")
        if not isinstance(noise_type, str) or noise_type not in self.NOISE_TYPES:
            raise ValueError(f"Rule {index} has unknown noise type: {noise_type!r}")
        scale = self._number(noise.get("scale", 100), f"Rule {index} noise scale", minimum=1e-9)
        octaves = self._integer(noise.get("octaves", 1), f"Rule {index} octaves", minimum=1)
        persistence = self._number(noise.get("persistence", 0.5), f"Rule {index} persistence", minimum=1e-9)
        lacunarity = self._number(noise.get("lacunarity", 2), f"Rule {index} lacunarity", minimum=1e-9)
        seed_offset = self._integer(noise.get("seed_offset", 0), f"Rule {index} seed_offset")
        if noise_type in {"white", "worley"} and octaves != 1:
            raise ValueError(f"Rule {index} {noise_type} noise supports one octave")

        return {
            "object_type": object_type,
            "params": params.copy(),
            "count": count,
            "range": (low, high),
            "noise": noise_type,
            "scale": scale,
            "octaves": octaves,
            "persistence": persistence,
            "lacunarity": lacunarity,
            "seed": self.seed + seed_offset,
        }

    def generate(self, world):
        if not self.enabled:
            return []
        if world.width <= 0 or world.height <= 0:
            raise ValueError("World dimensions must be positive")

        cells = []
        for y0 in range(0, int(world.height), self.cell_size):
            y = y0 + min(self.cell_size, world.height - y0) / 2
            for x0 in range(0, int(world.width), self.cell_size):
                x = x0 + min(self.cell_size, world.width - x0) / 2
                cells.append((x, y))

        placements = {}
        for index, rule in enumerate(self.rules):
            if rule["count"] == 0:
                continue
            candidates = []
            low, high = rule["range"]
            for cell_index, (x, y) in enumerate(cells):
                if cell_index in placements:
                    continue
                value = self._sample(rule, x, y)
                if low <= value <= high:
                    candidates.append((value, cell_index))
            if rule["count"] is not None:
                candidates.sort(key=lambda candidate: (-candidate[0], candidate[1]))

            placed = 0
            for _, cell_index in candidates:
                x, y = cells[cell_index]
                cls = self.registry[rule["object_type"]]
                try:
                    entity = cls(x=x, y=y, **rule["params"])
                except TypeError as exc:
                    raise ValueError(f"Invalid params for {rule['object_type']!r}") from exc
                if world.type == "bounded":
                    rect = entity.get_rect()
                    if rect.left < 0 or rect.top < 0 or rect.right > world.width or rect.bottom > world.height:
                        continue
                placements[cell_index] = entity
                placed += 1
                if placed == rule["count"]:
                    break
            if rule["count"] is not None and placed < rule["count"]:
                raise ValueError(
                    f"Rule {index} requested count={rule['count']}, but only {placed} valid cells are available"
                )
        return [placements[index] for index in sorted(placements)]

    def _sample(self, rule, x, y):
        x /= rule["scale"]
        y /= rule["scale"]
        kind = rule["noise"]
        seed = rule["seed"]
        if kind == "white":
            return self._hash(math.floor(x), math.floor(y), seed)
        if kind == "worley":
            return self._worley(x, y, seed)

        total = 0.0
        amplitude = 1.0
        amplitude_sum = 0.0
        frequency = 1.0
        sampler = self._value if kind == "value" else self._perlin
        for _ in range(rule["octaves"]):
            total += sampler(x * frequency, y * frequency, seed) * amplitude
            amplitude_sum += amplitude
            amplitude *= rule["persistence"]
            frequency *= rule["lacunarity"]
        return min(1.0, max(0.0, total / amplitude_sum))

    @staticmethod
    def _hash(x, y, seed):
        value = (x * 374761393 + y * 668265263 + seed * 1442695041) & 0xFFFFFFFF
        value = ((value ^ (value >> 13)) * 1274126177) & 0xFFFFFFFF
        return ((value ^ (value >> 16)) & 0xFFFFFFFF) / 0xFFFFFFFF

    @staticmethod
    def _fade(value):
        return value * value * value * (value * (value * 6 - 15) + 10)

    @staticmethod
    def _lerp(a, b, amount):
        return a + (b - a) * amount

    def _value(self, x, y, seed):
        ix, iy = math.floor(x), math.floor(y)
        tx, ty = self._fade(x - ix), self._fade(y - iy)
        lower = self._lerp(self._hash(ix, iy, seed), self._hash(ix + 1, iy, seed), tx)
        upper = self._lerp(self._hash(ix, iy + 1, seed), self._hash(ix + 1, iy + 1, seed), tx)
        return self._lerp(lower, upper, ty)

    def _perlin(self, x, y, seed):
        ix, iy = math.floor(x), math.floor(y)
        tx, ty = x - ix, y - iy
        gradients = ((1, 0), (-1, 0), (0, 1), (0, -1),
                     (math.sqrt(0.5), math.sqrt(0.5)),
                     (-math.sqrt(0.5), math.sqrt(0.5)),
                     (math.sqrt(0.5), -math.sqrt(0.5)),
                     (-math.sqrt(0.5), -math.sqrt(0.5)))

        def dot(cx, cy, dx, dy):
            index = min(7, int(self._hash(cx, cy, seed) * 8))
            gx, gy = gradients[index]
            return gx * dx + gy * dy

        lower = self._lerp(dot(ix, iy, tx, ty), dot(ix + 1, iy, tx - 1, ty), self._fade(tx))
        upper = self._lerp(dot(ix, iy + 1, tx, ty - 1), dot(ix + 1, iy + 1, tx - 1, ty - 1), self._fade(tx))
        return min(1.0, max(0.0, 0.5 + self._lerp(lower, upper, self._fade(ty))))

    def _worley(self, x, y, seed):
        ix, iy = math.floor(x), math.floor(y)
        nearest = math.inf
        for cy in range(iy - 1, iy + 2):
            for cx in range(ix - 1, ix + 2):
                fx = cx + self._hash(cx, cy, seed)
                fy = cy + self._hash(cx, cy, seed + 1)
                nearest = min(nearest, math.hypot(x - fx, y - fy))
        return 1.0 - min(1.0, nearest / math.sqrt(2))
