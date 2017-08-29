"""
Movement and robot enivronment data

:Contains: `RobotEnv`, `Move`
"""

from typing import NamedTuple
from enum import Enum

class RoboEnv(NamedTuple):
    """
    Stores data about robot's immediate environment

    Each direction should be `True` if there is an empty cell immediately
     that direction, and `False` if the edge or an obstacle is there.

    :extends: `NamedTuple`

    :Attributes:
       - `front`: Whether the robot can move forwards - bool
       - `right`: Whether the robot can move right - bool
       - `back`: Whether the robot can move backwards - bool
       - `left`: Whether the robot can move left - bool
    """
    front: bool
    right: bool
    back: bool
    left: bool

class Move(Enum):
    """
    Robot movement command

    Each enumerate value represents a movement command in
     the direction indicated by the name.
    """
    FORWARD = 0
    RIGHT = 1
    BACKWARD = 2
    LEFT = 3
