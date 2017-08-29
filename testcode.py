"""
Code testing screen with menu bar and grid

:Contains: `TestCode`
"""

import importlib
import sys

from kivy.clock import Clock
from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty

from board import Board
from movement import Move


# 'path' is user-created code, so each time it is
#  imported/reloaded/used it must be within a
#  try/except block so user errors cannot crash the app
try:
    import path
except:
    # Bad user code could throw pretty much any error,
    #  and we don't want to let it crash the app,
    #  so Gotta Catch 'Em All!
    pass


class TestCode(Screen):
    """
    Code testing screen with grid display, code execution and menu (ActionBar)
    """

    message = StringProperty("")
    board_file = StringProperty("")

    def __init__(self, *args, **kwargs):
        """
        Initialize TestCode

        :Properties:
           - `message`: Message to display to user - default `""`
           - `board_file`: Name of file to use as source for board - default `""`
        """

        super(TestCode, self).__init__(*args, **kwargs)

        # Pixel size of grid
        self.grid_size = 600
        # Pixel size of action bar at top of grid
        self.action_bar_height = 48

        # Number of separator lines in grid
        self.num_lines = 19
        # Number of row/columns in grid
        self.num_spaces = self.num_lines + 1

        # Delay in seconds between each update
        self.path_execution_speed = 0.08

        # Reference to grid widget
        self.grid = None

        # Handle to Kivy Clock scheduling object
        self.path_update = None

        # bool tracking whether user code module 'path' is successfully loaded
        self.path_loaded = self.check_path_module()

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
        self._init_grid()

    def _init_grid(self):
        # Clear grid - remove all obstacles
        self.grid.clear()

        # Set obstacles in grid
        for cell, x_index, y_index in self.game_board.board_cells():
            if cell == 1:
                self.grid.set_obstacle(x_index, y_index)

        # Set start/end positions on board
        self.start = self.game_board.get_start()
        self.end = self.game_board.get_end()
        self.grid.set_start(self.start[0], self.start[1])
        self.grid.set_end(self.end[0], self.end[1])

    def edit_code(self):
        """
        Switch to edit screen
        """
        self.manager.current = 'EditCode'

    def menu(self):
        """
        Return to main menu screen
        """
        self.manager.current = 'Menu'

    def on_pre_enter(self, *args):
        """
        Overriden `Screen` method called before screen is switched to

        Used to reset grid when grid screen is loaded.
        """
        super(TestCode, self).on_pre_enter(*args)
        self.game_board.load_from_file(self.board_file)
        self._init_grid()
        self.reset()

    def check_path_module(self):
        """
        Check if user code in path module is loaded

        :Returns: `True` if path is loaded is, `False` otherwise
        """
        try:
            path_module = sys.modules["path"]
            return True
        except KeyError:
            return False

    def load_path_code(self):
        """
        Load user code in path module
        """
        # If the module has been successfuly loaded, reload it
        if self.path_loaded:
            try:
                path = sys.modules["path"]
                importlib.reload(path)
            # Could not reload path module, user code has errors
            except:
                self.message = "Can't load path code."
                self.path_loaded = False
        # Otherwise try to import it
        else:
            try:
                import path
                self.path_loaded = self.check_path_module()
            # Could not import path module, user code has errors
            except:
                # Something is broken in the code
                self.message = "Can't load path code."
                self.path_loaded = False

    def reset_board(self):
        """
        Reset robot position on board
        """
        self.game_board.reset_robot()

    def pause(self):
        """
        Pause execution of user path code
        """
        if self.path_update:
            self.path_update.cancel()
            self.path_update = None

    def start_path(self):
        """
        Start execution of user path code
        """
        # If the robot is at end of path, reset grid before starting path code again
        if self.game_board.get_robot_position() == self.game_board.get_end():
            self.reset()
        if not self.path_update:
            self.path_update = Clock.schedule_interval(
                self.update, self.path_execution_speed)

    def reset(self):
        """
        Reset grid
        """
        # Stop path execution
        self.pause()
        # Reset robot position in internal board represenation
        self.reset_board()
        # Reset error message
        self.message = ''
        # Reload user code in path module
        self.load_path_code()
        # Reset robot on grid display
        self.grid.reset_robot()

    def update(self, dt=0):
        """
        Update robot with new move command from path code

        `dt` is argument for `Clock` scheduling, leave as default.
        """
        # Get data about robot's immediate environment
        robot_env = self.game_board.get_robot_env()
        # Move directive
        move = None

        # Get move command from user code, wrapped in try/except
        #  to prevent buggy user code from crashing app
        try:
            if self.path_loaded:
                # Update Robot's environment data
                path.Robot.environment = robot_env
                # Get move directive from user
                move = path.Robot.get_move()
            else:
                self.message = "Path code is not loaded."
                self.pause()
        # Print error message if syntax error
        except SyntaxError as error:
            self.message = "Error on line " + str(error.lineno)
            print(error)
            self.pause()
            return
        except:
            self.message = "Error in code"
            print("Non-syntax error in user code.")
            self.pause()
            return

        # Ensure move directive is valid command (instance of Move enum)
        if isinstance(move, Move):
            # Execute directive
            robot_pos = self.game_board.make_move(move)
            self.grid.set_robot(robot_pos)

            if self.game_board.get_robot_position() == self.game_board.get_end():
                self.pause()
        else:
            self.message = "Error in code"
            self.pause()
