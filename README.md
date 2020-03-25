# PyWeek 29 - Butterfly Effect

Team lead by Piper Thunstrom

Written with [ppb](https://ppb.dev)

## Dev instructions

1. Make a local virtual environment in your preferred method.
2. Activate your virtual environment
3. `pip install -e .`

To run the game:

    python -m butterfly_effect

To debug a specific scene without going through the graph:

    python -m butterfly_effect -s ${chosen_scene}

The scene in question must be included in the scene_map in
`butterfly_effect.__init__.py` to be used in this manner.
