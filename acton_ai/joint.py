from dataclasses import dataclass


@dataclass
class Joint:
    """A helper class to store information about a joint on the robot."""

    joint_id: int
    flip: bool = False
    left_buffer: int = 0
    """This is the buffer to add to the joint minimum to prevent the robot from hitting
    the physical limits, in degrees. Joint ID 2 especially seemed to need this."""

    right_buffer: int = 0
    """This the buffer angle to subtract from the robots reported joint max, when
    setting the joint angles."""

    scaling_factor: float = 1.0
    """This is a scaling factor to apply to the joint angles. This is useful for
    adjusting grippers, if you want to have small motions lead to larger motions, or
    vice versa."""

    @property
    def array_idx(self) -> int:
        return self.joint_id - 1

    def apply_transform(self, angle: float) -> float:
        """Apply the joint's transform to the angle."""
        direction = -1 if self.flip else 1
        return direction * angle * self.scaling_factor
