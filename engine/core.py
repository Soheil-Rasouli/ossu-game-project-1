from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    Optional,
    Tuple,
)

import arcade
import arcade.tilemap

from engine import (
    game_state,
    scripts,
    spec,
)
from engine.gui import game_state as gui_game_state
from engine.ingame import game_state as ingame_state
from engine.model import world

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 650
SCREEN_TITLE = "OSSU Game Project"


class GameNotInitializedError(Exception):
    """Raised when functions are called before the game was properly initialized."""


class Core(arcade.Window):
    """
    Main application class, wraps everything.

    The game uses an MVC pattern:
    * Model - capture the state of the world in the game: players, regions, enemies,
      etc.
    * Views - handle rendering anything.
    * Controllers - handles interacting with the user.

    There's only one model, but the views and controllers are wrapped by GameState
    objects. The game can be in one of two possible states:
    * In a GUI - the model does not update, we render some sort of GUI, and all controls
      go to manipulating the GUI.
    * In the game - the model updates and all controls go to managing the character.
    """

    current_state: Optional[game_state.GameState]
    gui_state: gui_game_state.GuiState
    ingame_state: Optional[ingame_state.InGameState]

    world: Optional[world.World]
    initial_gui: scripts.GUI
    ingame_gui: Optional[scripts.GUI]
    initial_player_state: Dict[str, Any]
    _spec: spec.GameSpec

    def __init__(
        self,
        initial_gui: Callable[[scripts.GameAPI], scripts.GUI],
        game_spec: spec.GameSpec,
        initial_player_state: Dict[str, Any],
        ingame_gui: Optional[Callable[[scripts.GameAPI], scripts.GUI]] = None,
    ):
        """Constructor.

        Args:
            initial_gui: The GUI screen to show when the game starts.
        """
        super().__init__(
            SCREEN_WIDTH,
            SCREEN_HEIGHT,
            SCREEN_TITLE,
        )

        self._spec = game_spec
        self.world = None
        self.initial_gui = initial_gui(self)
        self.ingame_gui = ingame_gui(self) if ingame_gui else None
        self.initial_player_state = initial_player_state
        self.gui_state = gui_game_state.GuiState(self, self.initial_gui)
        self.ingame_state = None
        self.current_state = None

    def setup(self) -> None:
        """Resets the game state."""
        self.gui_state.setup()

    def start_game(self) -> None:
        """Switches to the "in game" state."""
        if self.world is None:
            self.world = world.World(self, self._spec, self.initial_player_state)

        if self.ingame_state is None:
            self.ingame_state = ingame_state.InGameState(
                self.world,
                (self.width, self.height),
                self.ingame_gui,
            )
            self.ingame_state.setup()

        self.current_state = self.ingame_state

    def change_region(self, name: str, start_location: str) -> None:
        """Changes the region of the game."""
        if self.world is None:
            raise GameNotInitializedError()

        self.world.load_region(name, start_location)

    def show_gui(self, gui: scripts.GUI) -> None:
        """Switches to the "GUI" state, and displays a certain GUI."""
        self.gui_state.set_gui(gui)
        self.current_state = self.gui_state

    def create_sprite(
        self,
        spec_name: str,
        name: str,
        start_location: Tuple[int, int],
        script: Optional[scripts.Script],
    ) -> None:
        """Creates a sprite."""
        if self.world is None:
            raise GameNotInitializedError()

        _spec = self._spec.sprites[spec_name]
        self.world.create_sprite(_spec, name, start_location, script)

    def get_key_points(self, name: Optional[str] = None) -> Iterable[scripts.KeyPoint]:
        """Queries for key points in the current region."""
        if self.world is None:
            raise GameNotInitializedError()

        return self.world.get_key_points(name)

    @property
    def player_state(self) -> Dict[str, Any]:
        """Gets the player's state."""
        if self.world is None:
            raise GameNotInitializedError()

        return self.world.player_state

    @player_state.setter
    def player_state(self, value: Dict[str, Any]):
        """Sets the player's state."""
        if self.world is None:
            raise GameNotInitializedError()

        self.world.player_state = value

    def run(self):
        """Runs the game."""
        self.setup()
        self.show_gui(self.initial_gui)
        arcade.run()

    ############################################################################
    # The rest of the methods are there to tie into Arcade's input and rendering
    # system. For the most part they are just delegates to the appropriate
    # object.
    ############################################################################

    def on_draw(self) -> None:
        """Renders the game."""
        if self.current_state is None:
            raise GameNotInitializedError()

        self.clear()
        self.current_state.view.on_draw()

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        """Handles incoming key presses."""
        if self.current_state is None:
            raise GameNotInitializedError()

        self.current_state.controller.on_key_press(symbol, modifiers)

    def on_key_release(self, symbol: int, modifiers: int) -> None:
        """Handles incoming key releases."""
        if self.current_state is None:
            raise GameNotInitializedError()

        self.current_state.controller.on_key_release(symbol, modifiers)

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int) -> None:
        """Handles mouse movement."""
        if self.current_state is None:
            raise GameNotInitializedError()

        self.current_state.controller.on_mouse_motion(x, y, dx, dy)

    def on_mouse_release(
        self,
        x: int,
        y: int,
        button: int,
        modifiers: int,
    ) -> None:
        """Handles releasing the mouse button."""
        if self.current_state is None:
            raise GameNotInitializedError()

        self.current_state.controller.on_mouse_release(
            x,
            y,
            button,
            modifiers,
        )

    def on_update(self, delta_time: float) -> None:
        """Handles updates."""
        if self.current_state is None:
            raise GameNotInitializedError()

        self.current_state.on_update(delta_time)
