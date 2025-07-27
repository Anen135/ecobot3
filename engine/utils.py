# utils.py

class Timer:
    """
    Таймер, основанный на времени (в секундах).
    Используется для отслеживания продолжительности событий.
    """
    def __init__(self, duration: float):
        """
        :param duration: Длительность таймера в секундах
        """
        self.duration = duration
        self.elapsed = 0.0
        self.active = True

    def update(self, dt: float):
        """
        Обновление таймера, добавляется прошедшее время.
        :param dt: Дельта времени в секундах
        """
        if self.active:
            self.elapsed += dt

    def is_done(self) -> bool:
        """
        Проверяет, истёк ли таймер.
        """
        return self.elapsed >= self.duration

    def reset(self):
        """
        Сброс таймера.
        """
        self.elapsed = 0.0
        self.active = True

    def stop(self):
        """
        Останавливает таймер без сброса.
        """
        self.active = False

    def resume(self):
        """
        Возобновляет таймер.
        """
        self.active = True


class StepCounter:
    """
    Счётчик дискретных шагов (тиков симуляции).
    """
    def __init__(self, max_steps: int = None):
        """
        :param max_steps: Максимальное количество шагов (необязательное ограничение)
        """
        self.steps = 0
        self.max_steps = max_steps

    def increment(self, amount: int = 1):
        """
        Увеличить счётчик шагов.
        :param amount: на сколько увеличить (по умолчанию 1)
        """
        self.steps += amount

    def is_done(self) -> bool:
        """
        Проверяет, достигнут ли лимит шагов.
        """
        return self.max_steps is not None and self.steps >= self.max_steps

    def reset(self):
        """
        Сброс счётчика шагов.
        """
        self.steps = 0
