# EcoBot3

**v0.1.0-beta.1** · A configurable 2D simulation with an agent that learns through reinforcement learning while the simulation runs.

Built with Python, Pygame CE and NumPy. This beta enables the neural controller and a wraparound (`torus`) world by default.

## Features

- **Runtime reinforcement learning:** a DQN controller with experience replay, a target network and epsilon-greedy exploration.
- **Ray-based perception:** 24 configurable rays detect distances and distinguish food, obstacles, world boundaries and other entities.
- **Movement:** nine combinations of forward/backward/idle movement and left/right/idle turning, including simultaneous movement and turning.
- **Rewards:** food collection is rewarded; elapsed time and blocked movement are penalized.
- **Procedural worlds:** configurable noise-based placement and object counts using the entity registry.
- **Game loop modes:** keep the world, regenerate it, or restore the same layout after all food is collected. Agent position and score retention are configurable.
- **Debug display:** rays, training updates, replay size, exploration rate, loss and reward.
- **Alternative controllers:** keyboard, mouse, rotating and food-seeking AI.

## Run

Tested with Python 3.14.7 on Windows.

```powershell
git clone https://github.com/Anen135/ecobot3.git
cd ecobot3
python -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe main.py
```

On macOS/Linux, use `venv/bin/python` in place of `.\venv\Scripts\python.exe`.
Run commands from the repository root. Press **Esc** or close the window to exit.

## Configuration

| File | Settings |
| --- | --- |
| `config/agent_config.json` | Controller, movement speeds, rays, network size, training and rewards |
| `config/world_config.json` | World size and `bounded`, `infinite` or `torus` topology |
| `config/generation_config.json` | Procedural generation, noise, seeds and object counts |
| `config/game_loop_config.json` | `none`, `regenerate`, `restart_same`, position reset and score retention |
| `config/engine_config.json` | Config file bindings, debug display, timing and static object loading |

The default controller is `nn`. Learning starts after 128 collected transitions. Network weights, replay memory and exploration state survive world resets within the same application session.

## Beta limitations

- The network starts untrained and initially explores randomly. Successful navigation or convergence is not guaranteed.
- Learning state is held in memory and is **not saved when the application closes**.
- Sparse food rewards and world configuration can make training slow.

## Tests

```powershell
.\venv\Scripts\python.exe -m unittest discover -s tests -v
```

The suite covers controllers, procedural generation, world behavior, game loop resets, ray intersections and runtime learning.
