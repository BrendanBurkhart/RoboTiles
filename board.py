"""
Functionality for tracking represenation of 2D robot grid

:Contains: `Board`
"""

from tokenizer import tokenize
from movement import Move, RoboEnv


class Board:
    """
    Represents a board for robot control game
    """

    def __init__(self, size: int, source_file: str):
        """
        Initialize the board

        :Args:
           - `size`: Linear size of the board (it will be square)
           - `source_file`: String name of file to use as source for the board

        :Raises:
           - FileNotFoundError: The specified `source_file` does not exist or is invalid
           - RuntimeError: The file contained illegal tokens, did not match the
            dimensions specified by `size`, or did not specify both a start and end position.
        """
        self.size = size

        self.load_from_file(source_file)

    def board_cells(self):
        """
        Get the value of each cell on the board

        :Yields: 3-tuple with the cell value, x index, y index of each cell.
        Cell value is `0` to signify empty cell, `1` to signify obstacle.
        """
        for y_index, row in enumerate(self.board):
            for x_index, cell_value in enumerate(row):
                yield (cell_value, x_index, y_index)

    def load_from_file(self, source_file: str):
        """
        (Re-)Load board layout from `source_file`

        :Args:
           - `source_file`: String name of file to load board from

        :Raises:
           - FileNotFoundError: The specified `source_file` does not exist or is invalid
           - RuntimeError: The file contained illegal tokens, did not match the
            dimensions specified by `size`, or did not specify both a start and end position.
        """
        # Keywords for tokenizer
        keywords = {"0", "1", "START", "END"}

        try:
            tokens = tokenize(source_file, keywords, False)
        except FileNotFoundError:
            raise FileNotFoundError(
                "File supplied to Board is invalid or does not exist!")
        except RuntimeError as error:
            raise RuntimeError(
                "File supplied to board contains illegal token(s) at line " +
                str(error.args[0]) + "!")

        try:
            # start/end are (x, y) tuples for the position of the start
            #  and end positions. board is a size by size row major
            #  matrix representing the board.
            self.start, self.end, self.board = self._fill_board_matrix(tokens)
        except RuntimeError:
            raise RuntimeError("File supplied to board does not match dimensions specified" +
                               "by size, or does not specify both a start and an end position.")

        # List with (x, y) coords for current robot position
        self.robot_position = [self.start[0], self.start[1]]

    def save_to_file(self, save_file: str):
        """
        Save board layout to `save_file`

        :Args:
           - `save_file`: String name of file to save board to

        :Raises:
           - FileNotFoundError: The specified `save_file` does not exist or is invalid
        """

        save_data = ""

        for y_index, row in enumerate(self.board):
            for x_index, cell_value in enumerate(row):
                if y_index == self.start[1] and x_index == self.start[0]:
                    save_data += "start "
                elif y_index == self.end[1] and x_index == self.end[0]:
                    save_data += "end "
                else:
                    save_data += (str(cell_value) + " ")
            save_data += "\n"

        try:
            with open(save_file, 'w') as code_file:
                code_file.write(save_data)
                code_file.truncate()
        except FileNotFoundError:
            raise FileNotFoundError("Could not save board to file.")

    def get_start(self):
        """
        Get position of start cell on board

        :Return: Start position on board as (`x`, `y`) tuple
        """
        return self.start

    def get_end(self):
        """
        Get position of end cell on board

        :Return: End position on board as (`x`, `y`) tuple
        """
        return self.end

    def get_robot_env(self):
        """
        Get data about the robot's immediate environment

        :Returns: `RoboEnv` object holding data about the robot's immediate surroundings.
        """
        front = False
        right = False
        back = False
        left = False

        if self.robot_position[1] < self.size - 1 and not self.board[self.robot_position[1] +
                                                                     1][self.robot_position[0]]:
            front = True
        if self.robot_position[0] < self.size - 1 and not self.board[self.robot_position[1]
                                                                     ][self.robot_position[0] + 1]:
            right = True
        if self.robot_position[1] > 0 and not self.board[self.robot_position[1] -
                                                         1][self.robot_position[0]]:
            back = True
        if self.robot_position[0] > 0 and not self.board[self.robot_position[1]
                                                         ][self.robot_position[0] - 1]:
            left = True

        return RoboEnv(front, right, back, left)

    def get_robot_position(self):
        """
        Get current robot position

        :Returns: (`x`, `y`) tuple of current robot position
        """
        return (self.robot_position[0], self.robot_position[1])

    def make_move(self, move: Move):
        """
        Execute robot movement command

        If the move would place the robot off board, or in an obstacle
        the robot will stay put.

        :Args:
           - `move`: `Move` value specifying robot move

        :Returns: (`x`, `y`) tuple of robot's updated position
        """
        move_vector = None
        if move == Move.FORWARD:
            move_vector = [0, 1]
        elif move == Move.LEFT:
            move_vector = [-1, 0]
        elif move == Move.RIGHT:
            move_vector = [1, 0]
        else:
            move_vector = [0, -1]

        x_pos = self.robot_position[0] + move_vector[0]
        y_pos = self.robot_position[1] + move_vector[1]
        x_pos, y_pos = self._limit_pos(x_pos, y_pos)

        if not self.board[y_pos][x_pos]:
            self.robot_position[0] = x_pos
            self.robot_position[1] = y_pos
        return (self.robot_position[0], self.robot_position[1])

    def reset_robot(self):
        """
        Reset robot to the starting position
        """
        self.robot_position[0] = self.start[0]
        self.robot_position[1] = self.start[1]

    def set_obstacle(self, x_pos: int, y_pos: int):
        """
        Set the cell at (`x_pos`, `y_pos`) to be an obstacle

        :Args:
           - `x_pos`: x position of obstacle to set
           - `y_pos`: y position of obstacle to set

        :Raises:
           - `RuntimeError`: Obstacle cannot be set at start or end cells
        """
        start_check = ((x_pos != self.start[0]) or (y_pos != self.start[1]))
        end_check = ((x_pos != self.end[0]) or (y_pos != self.end[1]))

        if start_check and end_check:
            self.board[y_pos][x_pos] = 1
        else:
            error_msg = "Tries to set board obstacle at "
            if not start_check:
                raise RuntimeError(error_msg + "start")
            else:
                raise RuntimeError(error_msg + "end")

    def remove_obstacle(self, x_pos: int, y_pos: int):
        """
        Remove obstacle (if it exists) at (`x_pos`, `y_pos`)

        :Args:
           - `x_pos`: x position of obstacle to remove
           - `y_pos`: y position of obstacle to remove

        :Raises:
           - `RuntimeError`: Obstacle cannot be removed at start or end cells
        """
        start_check = ((x_pos != self.start[0]) or (y_pos != self.start[1]))
        end_check = ((x_pos != self.end[0]) or (y_pos != self.end[1]))

        if start_check and end_check:
            self.board[y_pos][x_pos] = 0
        else:
            error_msg = "Tries to remove board obstacle at "
            if not start_check:
                raise RuntimeError(error_msg + "start")
            else:
                raise RuntimeError(error_msg + "end")

    def check_cell_for_obstacle(self, x_pos: int, y_pos: int):
        """
        Check if obstacle exists at (`x_pos`, `y_pos`)

        :Args:
           - `x_pos`: x position of obstacle to check for
           - `y_pos`: y position of obstacle to check for

        :Returns: `True` if cell contains obstacle, `False` otherwise
        """
        if self.board[y_pos][x_pos] == 1:
            return True
        return False

    def _fill_board_matrix(self, tokens: list):
        """
        Initialize and populate a matrix to represent the board

        :Args:
           - `tokens`: List of tokens in the order found in the source file

        :Returns: `start`, `end` and `matrix`
         representing the board

        :Raises:
           - RuntimeError: `tokens` did not match the dimensions specified
            by `self.size`, or did not specify both a start and end position.
        """

        matrix = []

        # Start and end positions on board. Once found in the
        #  token list, these will be (x, y) tuples
        start = None
        end = None

        # Iterate through tokens and populate matrix, find start/end
        for y_index in range(self.size):
            row = []
            for x_index in range(self.size):
                try:
                    token = tokens[y_index * self.size + x_index]

                    # If the token is the start/end token, set the
                    #  start/end position on the board
                    if token.value == "START":
                        start = (x_index, y_index)
                        row.append(0)
                    elif token.value == "END":
                        end = (x_index, y_index)
                        row.append(0)
                    else:
                        # Convert from string rep. to int
                        value = 0 if token.value == "0" else 1
                        row.append(value)
                except IndexError:
                    raise RuntimeError(
                        "Specified board size does not match file.")
            matrix.append(row)

        # Check the both a start and an end token were found.
        if start and end:
            return start, end, matrix
        else:
            raise RuntimeError(
                "'source_file' must specify both the start and end positions!")

    def _limit_pos(self, x_pos: int, y_pos: int):
        """
        Get coordinates constrained to dimensions of the board

        :Args:
           - `x_pos`: integer x component of robot coords
           - `y_pos`: integer y component of robot coords

        :Returns: Coords (`x`, `y`) constrained to dimensions of board
        """
        if x_pos < 0:
            x_pos = 0
        elif x_pos >= self.size:
            x_pos = self.size - 1

        if y_pos < 0:
            y_pos = 0
        elif y_pos >= self.size:
            y_pos = self.size - 1

        return (x_pos, y_pos)
