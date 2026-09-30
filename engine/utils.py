
class Timer:
    def __init__(self, duration: float):
        self.duration = duration
        self.elapsed = 0.0
        self.active = True

    def update(self, dt: float):
        if self.active:
            self.elapsed += dt

    def is_done(self) -> bool:
        return self.elapsed >= self.duration

    def reset(self):
        self.elapsed = 0.0
        self.active = True

    def stop(self):
        self.active = False

    def resume(self):
        self.active = True


class StepCounter:
    def __init__(self, max_steps: int | None = None):
        self.steps = 0
        self.max_steps = max_steps

    def increment(self, amount: int = 1):
        self.steps += amount

    def is_done(self) -> bool:
        return self.max_steps is not None and self.steps >= self.max_steps

    def reset(self):
        self.steps = 0
