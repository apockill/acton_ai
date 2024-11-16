from acton_ai.connection_utilities import find_myarm_controller, find_myarm_motor
from acton_ai.logger import logger


def main() -> None:
    logger.info("Bringing up motors")
    controller = find_myarm_controller()
    mover = find_myarm_motor()

    # Get the mover in a known state
    mover.bring_up_motors()
    mover.prompt_user_to_bring_motors_into_bounds()

    while True:
        target_angles = controller.get_joint_angles_in_mover_space()
        mover.set_joints_from_controller_angles(target_angles, speed=100, debug=True)


if __name__ == "__main__":
    main()
