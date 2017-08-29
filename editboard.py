"""
Edit board grid

:Contains: `EditBoard`
"""

from kivy.clock import Clock
from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty

from board import Board

class EditBoard(Screen):
    """
    Board/grid editing screen
    """

    board_file = StringProperty("")

    def __init__(self, *args, **kwargs):
        """
        Initialize EditBoard

        :Properties:
           - `board_file`: String name of source file for board to edit - default `""`
        """

        super(EditBoard, self).__init__(*args, **kwargs)

        # Pixel size of grid
        self.grid_size = 600
        # Pixel size of action bar at top of grid
        self.action_bar_height = 48

        # Number of separator lines in grid
        self.num_lines = 19
        # Number of row/columns in grid
        self.num_spaces = self.num_lines + 1

        # Reference to grid widget
        self.grid = None

        # Internal rep of board - set in _init
        self.game_board = None

        self.start = (0, 0)
        self.end = (0, 0)

        # Kivy properties set in kv lang aren't available in __init__,
        #  schedule second stage of init after properties are set
        Clock.schedule_once(self._init)

    def _init(self, dt=0):
        """
        Second stage of initialization

        `dt` is argument for `Clock` scheduling, leave as default.
        """
        # Board representation
        self.game_board = Board(self.num_spaces, self.board_file)

        self.grid = self.ids.grid
        # Set obstacles in grid
        for cell, x_index, y_index in self.game_board.board_cells():
            if cell == 1:
                self.grid.set_obstacle(x_index, y_index)

        # Set start/end positions on board
        self.start = self.game_board.get_start()
        self.end = self.game_board.get_end()
        self.grid.set_start(self.start[0], self.start[1])
        self.grid.set_end(self.end[0], self.end[1])

    def tile_click(self, x_coord: int, y_coord: int):
        """
        Handle click on tile

        :Args:
           - `x_coord`: x coordinate of tile clicked in kivy coordinate space
           - `y_coord`: y coordinate of tile clicked in kivy coordinate space
        """

        # Convert from kivy GridLayout coords (standard Cartesian coords) to
        #  typical UI coords ((0, 0) is top left corner).
        y_coord = self.num_lines - y_coord

        start_check = (self.start[0] != x_coord) or (self.start[1] != y_coord)
        end_check = (self.end[0] != x_coord) or (self.end[1] != y_coord)

        if self.game_board.check_cell_for_obstacle(x_coord, y_coord):
            self.game_board.remove_obstacle(x_coord, y_coord)
            self.grid.remove_obstacle(x_coord, y_coord)
        elif start_check and end_check:
            self.game_board.set_obstacle(x_coord, y_coord)
            self.grid.set_obstacle(x_coord, y_coord)

        # Update board display
        self.grid.draw_grid()

    def menu(self):
        """
        Switch to main menu, and save board to file
        """
        self.save_board()

        self.manager.current = 'Menu'

    def save_board(self):
        """
        Save board to file
        """
        self.game_board.save_to_file(self.board_file)
