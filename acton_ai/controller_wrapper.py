from pymycobot import MyArmM

from .joint import Joint


class MotorsNotPoweredError(Exception):
    pass


class HelpfulMyArmC(MyArmM):
    """A wrapper around MyArmM that works around idiosyncrasies in the API"""

    # TODO: In the make this loadable as a per-robot configuration file.
    mover_joint_mapping = [
        Joint(joint_id=1, flip=True),
        Joint(joint_id=2, flip=True),
        Joint(joint_id=3, flip=True),
        Joint(joint_id=4, flip=True),
        Joint(joint_id=5, flip=False),
        Joint(joint_id=6, flip=True),
        Joint(joint_id=7, flip=False),
    ]
    """This maps joints from the MyArmC to the MyArmM, as observed by the author.
    Any value with a 5 was not found through empirical testing, and is arbitrary.
    """

    def get_joint_angles_in_mover_space(self) -> list[float]:
        """An API mirroring MyArmC.get_joints_angle, except it transforms the angles so
        they are in the space of the MyArmM, as observed by the author. This includes
        flipping the directions of certain joints which have been observed to be
        flipped, and scaling the angles of certain joints to make them more intuitive.
        """

        angles = self.get_joints_angle()
        return [
            joint.apply_transform(angle)
            for joint, angle in zip(self.mover_joint_mapping, angles, strict=False)
        ]
