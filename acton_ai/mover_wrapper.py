from functools import cached_property
from time import sleep
from typing import cast

from pymycobot import MyArmM

from acton_ai.logger import logger

from .joint import Joint


class MotorsNotPoweredError(Exception):
    pass


class HelpfulMyArmM(MyArmM):
    """A wrapper around MyArmM that works around idiosyncrasies in the API"""

    # TODO: In the make this loadable as a per-robot configuration file.
    joint_bounds = [
        Joint(joint_id=1, left_buffer=5, right_buffer=5),
        Joint(joint_id=2, left_buffer=20, right_buffer=10),
        Joint(joint_id=3, left_buffer=5, right_buffer=5),
        Joint(joint_id=4, left_buffer=5, right_buffer=5),
        Joint(joint_id=5, left_buffer=5, right_buffer=10),
        Joint(joint_id=6, left_buffer=5, right_buffer=5),
        Joint(joint_id=7, left_buffer=5, right_buffer=5),
    ]
    """This maps joints from the MyArmC to the MyArmM, as observed by the author.
    Any value with a 5 was not found through empirical testing, and is arbitrary.
    """

    @cached_property
    def bounded_joint_mins(self) -> tuple[int, ...]:
        mins = list(self.true_joint_mins)
        for joint in self.joint_bounds:
            mins[joint.array_idx] += joint.left_buffer
        return tuple(mins)

    @cached_property
    def bounded_joints_max(self) -> tuple[int, ...]:
        maxes = list(self.true_joints_max)
        for joint in self.joint_bounds:
            maxes[joint.array_idx] -= joint.right_buffer
        return tuple(maxes)

    @cached_property
    def true_joint_mins(self) -> tuple[int, ...]:
        return cast(tuple[int], tuple(self.get_joints_min()))

    @cached_property
    def true_joints_max(self) -> tuple[int, ...]:
        return cast(tuple[int], tuple(self.get_joints_max()))

    def clamp_angle(self, angle: float, joint: Joint) -> float:
        """Clamp an arbitrary angle to a given joint's limits"""
        max_angle = self.bounded_joints_max[joint.array_idx]
        min_angle = self.bounded_joint_mins[joint.array_idx]

        clamped = max(min_angle, min(max_angle, angle))
        return clamped

    def set_joints_from_controller_angles(
        self, controller_angles: list[float], speed: int, debug: bool = False
    ) -> None:
        """Set the joints of the robot from the controller angles

        :param controller_angles: The angles from the controller
        :param speed: The speed to set the joints
        :param debug: If true, does extra API calls to verify the movers joint positions
            are within the bounds set by the controller mapping. If they're not, this
            can manifest as a 'stuck' robot, where the robot is unable to move in any
            direction.
        """
        assert len(controller_angles) == len(
            self.bounded_joints_max
        ), "Incorrect number of angles"

        if debug:
            # This logs the motors that are out of bounds
            self.check_out_of_bounds_motors()

        for joint in self.joint_bounds:
            desired_angle: float = controller_angles[joint.array_idx]
            desired_angle = joint.apply_transform(desired_angle)
            desired_angle = self.clamp_angle(desired_angle, joint)
            controller_angles[joint.array_idx] = desired_angle

        self.set_joints_angle(controller_angles, speed)

    def check_out_of_bounds_motors(self) -> list[int]:
        """Returns a list of motor IDs that are out of bounds, if any"""

        motor_angles = self.get_joints_angle()
        out_of_bounds = []
        for joint in self.joint_bounds:
            angle = motor_angles[joint.array_idx]
            minimum = self.true_joint_mins[joint.array_idx]
            maximum = self.true_joints_max[joint.array_idx]
            if angle < minimum:
                logger.error(
                    f"Joint {joint.joint_id} is below the minimum: {angle=} {minimum=}"
                )
                out_of_bounds.append(joint.joint_id)
            if angle > maximum:
                logger.error(
                    f"Joint {joint.joint_id} is above the maximum: {angle=} {maximum=}"
                )
                out_of_bounds.append(joint.joint_id)
        return out_of_bounds

    def set_servos_enabled(self, state: bool) -> None:
        """Set all servos to the given state"""

        for joint in self.joint_bounds:
            self.set_servo_enabled(joint.joint_id, state)

    def prompt_user_to_bring_motors_into_bounds(self) -> None:
        """This function prompts the user to bring the motors into bounds"""

        self.set_servos_enabled(False)

        while True:
            out_of_bounds = self.check_out_of_bounds_motors()
            if not out_of_bounds:
                break
            logger.error(
                f"Motors {out_of_bounds} are out of bounds. Please adjust the motors"
            )
            sleep(1)

        logger.error("Locking servos!")
        self.set_servos_enabled(True)

    def bring_up_motors(self) -> None:
        """This sequence is designed to bring up the motors reliably"""
        # Sanity check communication is working
        assert self.is_robot_moving() == 0, "Robot is moving, what's going on?"
        assert self.get_robot_firmware_version() > 0

        # Turn on power
        self.set_robot_power_on()

        while True:
            # Author has observed first call can occasionally be None while subsequent
            # calls succeed.
            for _ in range(5):
                servo_status = self.get_servos_status()
                if servo_status is not None:
                    break

            if servo_status is None:
                logger.warning("Servos not working... Clearing errors and retrying")
                self.set_robot_power_off()
                sleep(0.25)
                self.set_robot_power_on()
                sleep(0.25)
                self.clear_robot_err()
                self.restore_servo_system_param()
                continue

            servos_unpowered = all(s == 255 for s in servo_status)
            if servos_unpowered:
                raise MotorsNotPoweredError(
                    "Servos are unpowered. Is the e-stop pressed?"
                )

            if all(s == 0 for s in servo_status):
                logger.info("Servos are good to go!")
                return
            else:
                raise MotorsNotPoweredError(f"Unexpected servo status: {servo_status}")
