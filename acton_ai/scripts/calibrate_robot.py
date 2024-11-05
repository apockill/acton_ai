from time import sleep

from acton_ai.connection_utilities import find_myarm_motor
from acton_ai.logger import logger


def main():
    mover = find_myarm_motor()
    mover.set_robot_power_on()

    # Get the mover in a zero state
    for i in range(7):
        mover.set_joint_angle(i + 1, angle=0, speed=10)
        sleep(0.5)

    logger.error(f"Joint Positions: {mover.get_joints_angle()}")

    input(
        f"Move joint {i + 1} to match the MyArmM. Then press 'Next' on the MyArmC'."
        f" Press Enter when finished."
    )


if __name__ == "__main__":
    main()
