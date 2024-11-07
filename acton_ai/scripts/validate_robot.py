from pymycobot import MyArmC, MyArmM

from acton_ai.connection_utilities import find_myarm_controller, find_myarm_motor
from acton_ai.logger import logger


def main() -> None:
    logger.info("Connecting to motors")
    controller = find_myarm_controller()
    mover = find_myarm_motor()

    logger.info("Controller information:")
    print_robot_info(controller)

    logger.info("Mover information:")
    print_robot_info(mover)


def print_robot_info(robot: MyArmM | MyArmC) -> None:
    logger.info(f"Python Version: {robot.check_python_version()}")
    logger.info(f"Robot Firmware Version: {robot.get_robot_firmware_version()}")
    logger.info(f"Robot Modified Version: {robot.get_robot_modified_version()}")
    logger.info(f"Tool Firmware Version: {robot.get_robot_tool_firmware_version()}")
    logger.info(f"Tool Modified Version: {robot.get_robot_tool_modified_version()}")


if __name__ == "__main__":
    main()
