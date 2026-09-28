# Collision System — Specification

> Status: **implemented**.
> This document duplicates the technical specification from [TODO.md](../TODO.md) and serves as
> an internal reference for implementation.

## 🎯 Goal

Implement an extensible collision system in which any game object can:

* participate in collisions;
* react to a collision differently depending on its type;
* block movement or not;
* interact selectively (for example, an agent with food, but not with the background).

---

## 🧱 Main components

### 1. Collision — the objects intersect

* Objects are checked for intersection of their physical shapes (by default — rectangular `Rect`).
* The shape is defined by the `get_rect()` method, which returns a `pygame.Rect`.
* `get_rect()` is already implemented for `Entity`, `Obstacle` (and inherited by `Food`, `Agent`).

### 2. Participation in collisions

* **All entities** take part in collision checks.
* Exception: visual or non-interactive effects — they can be excluded via logic (`skip_collision_check()`).

### 3. Reaction to a collision — via `on_collision(other, world)`

Each object implements its own collision-reaction logic:

```python
def on_collision(self, other: Entity, world: World):
    pass
```

* The object **decides itself** what to do when colliding with another one.
* Examples:

  * 🍎 **Food**: disappears when hit by an agent.
  * 🧱 **Obstacle**: cancels the agent's movement.
  * ☠️ **Enemy**: deals damage.
  * 🌀 **Zone**: changes the agent's state.
  * 🌟 **Effect**: ignores the collision (empty implementation).

### 4. The `blocks_movement` flag

* A separate flag (`True`/`False`) that determines whether the object blocks movement.
* Can be used to cancel movement:

```python
if other.blocks_movement:
    entity.revert_position()
```

> Note: `revert_position()` is implemented on `Entity` — it restores `x`/`y` to the position
> saved by `save_position()` at the start of the frame.

### 5. Collision handling in `World`

* The `handle_collisions()` method:

  * iterates over all pairs of objects;
  * checks `colliderect`;
  * calls `on_collision()` from both sides:

```python
entity.on_collision(other, self)
other.on_collision(entity, self)
```

---

## 🧪 Behavior examples

#### 🍎 Food

```python
class Food(Entity):
    def on_collision(self, other, world):
        if isinstance(other, Agent):
            other.score += 1
            world.entities.remove(self)
```

#### 🧱 Obstacle

```python
class Obstacle(Entity):
    blocks_movement = True

    def on_collision(self, other, world):
        if hasattr(other, 'revert_position'):
            other.revert_position()
```

#### ☠️ Enemy

```python
class Enemy(Entity):
    def on_collision(self, other, world):
        if isinstance(other, Agent):
            other.health -= 10
```

---

## 🔍 Extensions (optional)

* ✅ Circle collisions (`circle_radius`, `distance_to`)
* ✅ Layer-based collisions (`collision_layer`) and masks (`collides_with`)
* ✅ Processing priority control
* ✅ Exit events (e.g. `on_exit_collision()`)

---

## 📌 Requirements

* Collisions supported between all active objects.
* Reaction is defined via the `on_collision()` method, without hardcoding by type.
* Movement blocking must be possible.
* Flexibility for adding new object types with unique logic.

---

## Integration points in the current code

| Item | Where |
| --- | --- |
| `get_rect()` | Present for `Entity`, `Obstacle` (`Food` inherits from `Entity`) |
| `World.handle_collisions()` | In `engine/world.py`, called from `World.update(dt)` after movement |
| `on_collision()` | Empty method on `Entity`, overridden in subclasses (`Food`, `Obstacle`) |
| `blocks_movement` | Class-level flag on `Entity` (`False`); `True` for `Obstacle` |
| `revert_position()` | On `Entity` — restores `x`/`y` to the `save_position()` snapshot |
| `skip_collision_check()` | On `Entity` — returns `False`; effects can override it to `True` |