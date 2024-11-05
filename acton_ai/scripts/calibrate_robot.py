import logging

from acton_ai.connection_utilities import find_myarm_motor


def main():
    logging.basicConfig(level=logging.DEBUG)

    mover = find_myarm_motor()

    input(
        "Enter the 'Calibration' Menu of your MyArmC and select 'Calibrate Servos'."
        "Press Enter when ready."
    )

    mover.set_robot_power_on()
    for i in range(6):
        mover.set_joint_angle(i + 1, 0, 1)
        input(
            f"Move joint {i + 1} to match the MyArmM. Then press 'Next' on the MyArmC'."
            f" Press Enter when finished."
        )


if __name__ == "__main__":
    main()
