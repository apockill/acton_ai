from acton_ai.connection_utilities import find_myarm_controller, find_myarm_motor
from acton_ai.logger import logger


def main() -> None:
    logger.info("Bringing up motors")
    controller = find_myarm_controller()
    mover = find_myarm_motor()

    # Get the mover in a known state
    mover.bring_up_motors()

    while True:
        controller_angles = controller.get_joints_angle()
        mover.set_joints_from_controller_angles(controller_angles, speed=20)


if __name__ == "__main__":
    main()
