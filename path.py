# Leave this import alone
from movement import Move

class Robot:

    forward = 0

    @staticmethod
    def get_move():
        direction = (Robot.forward - 1) % 4
        while True:
            if direction == 0 and Robot.environment.front:
                Robot.forward = direction
                return Move.FORWARD
            if direction == 1 and Robot.environment.right:
                Robot.forward = direction
                return Move.RIGHT
            if direction == 2 and Robot.environment.back:
                Robot.forward = direction
                return Move.BACKWARD
            if direction == 3 and Robot.environment.left:
                Robot.forward = direction
                return Move.LEFT
            direction = (direction + 1) % 4
