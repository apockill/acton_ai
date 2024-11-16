"""**acton_ai**

My reppolicies for robot arms, and making them useful with multi-modal LLMs.
"""

__version__ = "0.2.0"

from pymycobot import MyArmC

from .connection_utilities import find_myarm_controller, find_myarm_motor
from .mover_wrapper import HelpfulMyArmM
