import json

from engine import (
    core,
    scripts,
)
from engine.gui import (
    spec_gui,
    widgets,
)


class StartScreen(spec_gui.SpecGUI):
    """Represents the start screen of the game."""

    def __init__(self, api: scripts.GameAPI):
        with open("assets/gui/start-screen.json") as infile:
            data = json.loads(infile.read())
            spec = widgets.GUISpec(
                dimensions=(core.SCREEN_WIDTH, core.SCREEN_HEIGHT),
                **data,
            )
            super().__init__(api, spec)


def start_game(api: scripts.GameAPI) -> None:
    """Starts the game."""
    api.start_game()
