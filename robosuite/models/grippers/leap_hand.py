"""
LEAP Hand
"""
import numpy as np

from robosuite.models.grippers.gripper_model import GripperModel
from robosuite.utils.mjcf_utils import xml_path_completion


class LEAP_Hand(GripperModel):
    """
    6-DoF Robotiq gripper.

    Args:
        idn (int or str): Number or some other unique identification string for this gripper instance
    """

    def __init__(self, idn=0):
        super().__init__(xml_path_completion("grippers/leap_hand.xml"), idn=idn)

    def format_action(self, action):
        return action

    @property
    def init_qpos(self):
        init = np.zeros(16) + 1
        return init
        np.array([
        # Index finger
        -0.1,    # if_mcp
         0.0,    # if_rot
        -0.5,    # if_pip
        -0.36,   # if_dip

        # Middle finger
        -0.1,    # mf_mcp
         0.0,    # mf_rot
        -0.5,    # mf_pip
        -0.36,   # mf_dip

        # Ring finger
        -0.1,    # rf_mcp
         0.0,    # rf_rot
        -0.5,    # rf_pip
        -0.36,   # rf_dip

        # Thumb
        -0.1,    # th_cmc
        -0.3,    # th_axl
        -0.4,    # th_mcp
        -1.2     # th_ipl
    ])

    @property
    def _important_geoms(self):
        return {
            "left_finger": [],
            "right_finger": [],
            "left_fingerpad": [],
            "right_fingerpad": [],
        }