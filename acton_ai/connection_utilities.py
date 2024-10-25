from pathlib import Path

from pymycobot import MyArmC, MyArmM
from serial import SerialException


class NoArmFoundError(Exception):
    pass

# If I ever add windows/mac support, this needs to be chosen based on platform.
_ARM_PORT_PATTERN = "ttyACM*"
_COMS_DIR = "/dev"

def _find_possible_ports() -> list[Path]:
    return list(Path(_COMS_DIR).glob(_ARM_PORT_PATTERN))


def _find_arm(arm_cls: type[MyArmC] | type[MyArmM]) -> MyArmC:
    check_ports = _find_possible_ports()
    exceptions: dict[Path, Exception] = {}
    for port in check_ports:
        try:
            # For some reason, the baudrate is required to be set to 1000000. The
            # default baudrate of the MyArmM is incorrect (115200)
            arm = arm_cls(str(port), baudrate="1000000")
        except SerialException as e:
            raise EnvironmentError(
                "There might be a permissions error. On linux, make sure you have added"
                " your user to the dialout group. \n"
                "Run`sudo chmod a+rw /dev/ttyACM*`, then try again."
            ) from e
        except Exception as e:  # noqa: BLE001
            exceptions[port] = (type(e), str(e))

        # This should be supported by both arms
        servo_statuses = arm.get_servos_status()
        is_controller = all(s == 0 for s in servo_statuses)

        if is_controller and arm_cls is MyArmC:
            print(f"Found MyArmC on port {port}")
            return arm
        elif not is_controller and arm_cls is MyArmM:
            print(f"Found MyArmM on port {port}")
            return arm
        else:
            exceptions[port] = (ValueError, f"Was a robot, but not type {arm_cls.__name__}")
            continue

    raise NoArmFoundError(
        f"No {arm_cls.__name__} controller found across ports.\n"
        f"Exceptions: {exceptions}"
    )


def find_myarm_motor() -> MyArmM:
    return _find_arm(MyArmM)


def find_myarm_controller() -> MyArmC:
    return _find_arm(MyArmC)
