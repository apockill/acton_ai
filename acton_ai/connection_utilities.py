from pathlib import Path
from typing import TypeVar

from pymycobot import MyArmC
from pymycobot.myarm_api import MyArmAPI
from serial import SerialException

from .logger import logger
from .mover_wrapper import HelpfulMyArmM

T = TypeVar("T", bound=MyArmAPI)


class NoArmFoundError(Exception):
    pass


# If I ever add windows/mac support, this needs to be chosen based on platform.
_ARM_PORT_PATTERN = "ttyACM*"
_COMS_DIR = "/dev"


def _find_possible_ports() -> list[Path]:
    return list(Path(_COMS_DIR).glob(_ARM_PORT_PATTERN))


def _find_arm(arm_cls: type[T]) -> T:
    check_ports = _find_possible_ports()
    exceptions: dict[Path, tuple[type[Exception], str]] = {}
    for port in check_ports:
        try:
            # For some reason, the baudrate is required to be set to 1000000. The
            # default baudrate of the MyArmM is incorrect (115200)
            arm = arm_cls(str(port), baudrate="1000000")
        except SerialException as e:
            raise OSError(
                "There might be a permissions error. On linux, make sure you have added"
                " your user to the dialout group. \n"
                "Run`sudo chmod a+rw /dev/ttyACM*`, then try again."
            ) from e
        except Exception as e:  # noqa: BLE001
            exceptions[port] = (type(e), str(e))

        # This should be supported by both arms
        try:
            servo_voltages = arm.get_servos_voltage()
            if servo_voltages is None:
                raise TypeError("Servo voltages were None")
        except TypeError as e:
            msg = "This is likely an arm, but may not be in communication mode."
            exceptions[port] = (type(e), str(e) + f": {msg}")
            continue

        # The Mover has servos that go above 20v, the controller does not.
        is_controller = all(s < 20 for s in servo_voltages)

        if is_controller and arm_cls is MyArmC:
            logger.info(f"Found MyArmC on port {port}")
            return arm  # type: ignore
        elif not is_controller and arm_cls is HelpfulMyArmM:
            logger.info(f"Found MyArmM on port {port}")
            return arm  # type: ignore
        else:
            exceptions[port] = (
                ValueError,
                f"Was a robot, but not type {arm_cls.__name__}",
            )
            continue

    exceptions_report = "\n".join(
        f"\tPort: {port}, Exception: {exc[0].__name__}, Message: {exc[1]}"
        for port, exc in exceptions.items()
    )
    raise NoArmFoundError(
        f"No {arm_cls.__name__} controller found across ports.\n"
        f"Exceptions:\n{exceptions_report}"
    )


def find_myarm_motor() -> HelpfulMyArmM:
    return _find_arm(HelpfulMyArmM)


def find_myarm_controller() -> MyArmC:
    return _find_arm(MyArmC)
