from dataclasses import dataclass
from functools import cached_property

from pymycobot import MyArmM

from acton_ai.logger import logger


class MotorsNotPoweredError(Exception):
    pass


@dataclass
class _Joint:
    joint_id: int
    flip: bool
    buffer: int
    """This is the buffer to add to the joint limits to prevent the robot from hitting 
    the physical limits, in degrees. Joint ID 2 especially seemed to need this."""

    @property
    def array_idx(self):
        return self.joint_id - 1


class HelpfulMyArmM(MyArmM):
    """A wrapper around MyArmM that works around idiosyncrasies in the API"""

    controller_joint_mapping = [
        _Joint(joint_id=1, flip=True, buffer=0),
        _Joint(joint_id=2, flip=True, buffer=10),
        _Joint(joint_id=3, flip=True, buffer=0),
        _Joint(joint_id=4, flip=True, buffer=0),
        _Joint(joint_id=5, flip=False, buffer=0),
        _Joint(joint_id=6, flip=True, buffer=0),
        _Joint(joint_id=7, flip=False, buffer=10),
    ]
    """This maps joints from the MyArmC to the MyArmM, as observed by the author"""

    @cached_property
    def joint_mins(self) -> list[int]:
        mins = self.get_joints_min()
        for joint in self.controller_joint_mapping:
            mins[joint.array_idx] += joint.buffer
        return mins

    @cached_property
    def joints_max(self) -> list[int]:
        maxes = self.get_joints_max()
        for joint in self.controller_joint_mapping:
            maxes[joint.array_idx] -= joint.buffer
        return maxes

    def clamp_angle(self, angle, joint: _Joint):
        """Clamp an arbitrary angle to a given joint's limits"""
        max_angle = self.joints_max[joint.array_idx]
        min_angle = self.joint_mins[joint.array_idx]

        clamped = max(min_angle, min(max_angle, angle))
        return clamped

    def set_joints_from_controller_angles(self, angles: list[int], speed: int) -> None:
        assert len(angles) == len(self.joints_max), "Incorrect number of angles"

        for joint in self.controller_joint_mapping:
            desired_angle = angles[joint.array_idx]
            if joint.flip:
                desired_angle = -desired_angle

            desired_angle = self.clamp_angle(desired_angle, joint)

            self.set_joint_angle(joint.joint_id, angle=desired_angle, speed=speed)

    def bring_up_motors(self) -> None:
        """This sequence is designed to bring up the motors reliably"""
        while True:
            servo_status = self.get_servos_status()

            servos_unpowered = all(s == 255 for s in servo_status)
            if servos_unpowered:
                raise MotorsNotPoweredError(
                    "Servos are unpowered. Is the e-stop pressed?"
                )

            if servo_status is None:
                logger.warning("Servos not working... Clearing errors and retrying")
                self.clear_robot_err()
                self.restore_servo_system_param()
                self.set_robot_power_on()
                self.clear_recv_queue()
                continue

            if all(s == 0 for s in servo_status):
                logger.info("Servos are good to go!")
                return
            else:
                raise MotorsNotPoweredError(f"Unexpected servo status: {servo_status}")