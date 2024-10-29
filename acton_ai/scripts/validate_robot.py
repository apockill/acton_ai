from pymycobot import MyArmC
from acton_ai.connection_utilities import find_myarm_motor, find_myarm_controller

# TODO: Add --port argument to the script
def main():
    controller = find_myarm_controller()
    print("Controller positions: ", controller.get_joints_angle())

    motor = find_myarm_motor()
    print("MyarmMotor positions: ", motor.get_joints_angle())


if __name__ == "__main__":
    main()
