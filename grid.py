"""
Display grid, with/out robot

:Contains: `Grid`
"""

from kivy.clock import Clock
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.properties import ListProperty
from kivy.properties import NumericProperty
from kivy.properties import BooleanProperty
from kivy.properties import ObjectProperty
from kivy.graphics import Color
from kivy.graphics import Line
from kivy.graphics import Rectangle


class Grid(GridLayout):
    """
    Kivy widget for visual display of grid, robot, start and end cells

    Callback can be set for cell click.
    """

    # Pixel size of whole grid
    grid_size = NumericProperty(0)
    # Number of separator lines in grid
    num_lines = NumericProperty(0)
    # Whether grid should track robot position and display robot tile
    with_robot = BooleanProperty(False)
    # Callback for tile/cell click/touch
    click_callback = ObjectProperty(None)

    def __init__(self, *args, **kwargs):
        """
        Initialize grid display

        :Properties:
           - `with_robot`: bool indicating whether the grid should display a
            robot tile - default `False`
           - `click_callback`: Callback for tile/cell click/touch - should accept two
            arguments with x and y coords of the tile clicked - default `None`
           - `grid_size`: Pixel size for whole grid - default `0`
           - `num_lines`: Number of separator lines in grif - default `0`
        """
        super(Grid, self).__init__(*args, **kwargs)

        self.obstacles = []

        # Pixel size of gaps between lines
        self.gap = 0

        # Number of lines + 1, the number of cells in one dimension of the grid
        self.num_spaces = 0

        self.start = [0, 0]
        self.end = [0, 0]

        self.robot_position = None

        # Kivy properties set in kv lang are not populated until *after* __init__ is finished,
        #  _init_ui is scheduled to run once the properties are populated
        Clock.schedule_once(self._init_tile_buttons)

    def _init_tile_buttons(self, dt=0):
        """
        Initializes buttons on grid, using callback set in `__init__`

        Second section of `__init__`, see comment in `__init__`.
         `dt` is argument for `Clock` scheduling, leave as default.
        """
        # Properties are set, set robot_position and click_callback
        if self.with_robot:
            self.robot_position = [0, 0]

        # Now that self.num_lines is set, set number of spaces
        self.num_spaces = self.num_lines + 1

        if self.click_callback:
            # Initialize grid of buttons/tiles
            for row in range(self.num_spaces):
                for column in range(self.num_spaces):
                    self.add_widget(TileButton(
                        coords=(column, row), release_callback=self.click_callback))

        # Kivy properties have been initialized
        self.draw_grid()

    def clear(self):
        """
        Remove all obstacles from grid
        """
        self.obstacles = []

    def set_obstacle(self, x_pos: int, y_pos: int):
        """
        Set a cell at (`x_pos`, `y_pos`) to be an obstacle

        Does nothing if the specified cell is the start or end cell.

        :Args:
           - `x_pos`: x position of obstacle to set
           - `y_pos`: y position of obstacle to set
        """
        obstacle = (x_pos, y_pos)

        start_check = ((obstacle[0] != self.start[0]) or (obstacle[1] != self.start[1]))
        end_check = ((obstacle[0] != self.end[0]) or (obstacle[1] != self.end[1]))

        if obstacle not in self.obstacles and start_check and end_check:
            self.obstacles.append(obstacle)

    def remove_obstacle(self, x_pos: int, y_pos: int):
        """
        Remove obstacle (if it exists) at (`x_pos`, `y_pos`)

        Does nothing if the specified cell is the start or end cell.

        :Args:
           - `x_pos`: x position of obstacle to remove
           - `y_pos`: y position of obstacle to remove
        """
        obstacle = (x_pos, y_pos)
        if obstacle in self.obstacles:
            self.obstacles.remove(obstacle)

    def set_start(self, x_pos: int, y_pos: int):
        """
        Set the start position cell

        :Args:
           - `x_pos`: x position of start cell
           - `y_pos`: y position of start cell
        """
        self.start[0] = x_pos
        self.start[1] = y_pos

    def set_end(self, x_pos: int, y_pos: int):
        """
        Set the end position cell

        :Args:
           - `x_pos`: x position of end cell
           - `y_pos`: y position of end cell
        """
        self.end[0] = x_pos
        self.end[1] = y_pos

    def set_robot(self, pos: tuple):
        """
        Set robot position to pos and update the graphics

        :Args:
           - `pos`: (x, y) tuple of position to set robot to
        """
        if self.with_robot:
            self.robot_position[0] = pos[0]
            self.robot_position[1] = pos[1]
            # Update graphics with new robot position
            self.draw_grid()
        else:
            raise RuntimeError("Grid.set_robot called on grid without robot")

    def reset_robot(self):
        """
        Reset robot back to starting position
        """
        if self.with_robot:
            self.robot_position[0] = self.start[0]
            self.robot_position[1] = self.start[1]
            # Update graphics with new robot position
            self.draw_grid()
        else:
            raise RuntimeError("Grid.reset_robot called on grid without robot")

    def draw_grid(self, dt=0):
        """
        Display grid, obstacles, start and end cells, and robot

        Recalculates grid spacing and layout.
         `dt` is argument for `Clock` scheduling, leave as default.
        """
        with self.canvas:
            # Clear widget's Kivy canvas
            self.canvas.clear()

            # Calculate gap between grid lines
            self.gap = self.grid_size / (self.num_spaces)

            Color(0, 0, 0, 1)  # Full black
            # Draw grid lines
            for i in range(self.num_lines):
                pos = self.gap * i + self.gap
                Line(points=[(0, pos), (self.grid_size, pos)], width=1.1)
                Line(points=[(pos, 0), (pos, self.grid_size)], width=1.1)

            Color(0.8, 0.1, 0.15, 0.9)  # Light/semi-transparent red
            # Draw obstacles
            for x_index, y_index in self.obstacles:
                Rectangle(
                    pos=(x_index * self.gap, y_index * self.gap), size=(self.gap, self.gap))

            # Draw start/end cells
            Color(0, 0, 0, 1)  # Full Black
            Rectangle(
                pos=(self.start[0] * self.gap, self.start[1] * self.gap),
                size=(self.gap, self.gap))
            Color(0, 1, 0, 1)  # Bright Green
            Rectangle(
                pos=(self.end[0] * self.gap, self.end[1] * self.gap),
                size=(self.gap, self.gap))

            if self.with_robot:
                # Set canvas color to dark brown
                Color(0.23, 0.2, 0.21, 1)
                # Draw robot
                Rectangle(
                    pos=(self.robot_position[0] * self.gap,
                         self.robot_position[1] * self.gap),
                    size=(self.gap, self.gap))


class TileButton(Button):
    """
    Clickable tile on grid
    """

    coords = ListProperty([0, 0])
    release_callback = ObjectProperty(None)

    def __init__(self, *args, **kwargs):
        """
        Initilaize TileButton

        :Properties:
          - `coords`: (x, y) coordinates of tile - default `[0, 0]`
          - `release_callback`: callback to call when the button is released - default `None`
        """

        super(TileButton, self).__init__(*args, **kwargs)

        # Bind callback to button release
        self.bind(on_release=self._execute_callback)

    def _execute_callback(self, obj):
        """
        Executes callback with arguments
        """
        self.release_callback(self.coords[0], self.coords[1])
