"""
Driver class for Keyboard controller.
"""

import glfw
import numpy as np
import copy

from robosuite.devices import Device
from robosuite.utils.transform_utils import rotation_matrix


class Keyboard(Device):
    """
    A minimalistic driver class for a Keyboard.

    Args:
        pos_sensitivity (float): Magnitude of input position command scaling
        rot_sensitivity (float): Magnitude of scale input rotation commands scaling
    """

    def __init__(self, pos_sensitivity=1.0, rot_sensitivity=1.0):

        self._display_controls()
        self._reset_internal_state(np.zeros(3))

        self._reset_state = 0
        self._enabled = False
        self._pos_step = 0.05

        self.alpha = 0.04
        self.alpha2 = 0.02

        self.pos_sensitivity = pos_sensitivity
        self.rot_sensitivity = rot_sensitivity

    @staticmethod
    def _display_controls():
        """
        Method to pretty print controls.
        """

        def print_command(char, info):
            char += " " * (10 - len(char))
            print("{}\t{}".format(char, info))

        print("")
        print_command("Keys", "Command")
        print_command("q", "reset simulation")
        print_command("spacebar", "toggle gripper (open/close)")
        print_command("w-a-s-d", "move arm horizontally in x-y plane")
        print_command("r-f", "move arm vertically")
        print_command("z-x", "rotate arm about x-axis")
        print_command("t-g", "rotate arm about y-axis")
        print_command("c-v", "rotate arm about z-axis")
        print_command("ESC", "quit")
        print("")

    def _reset_internal_state(self, init_pos):
        """
        Resets internal state of controller, except for the reset signal.
        """
        self.rotation = np.array([[-1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, -1.0]])
        self.raw_drotation = np.zeros(3)  # immediate roll, pitch, yaw delta values from keyboard hits
        self.last_drotation = np.zeros(3)
        # initialize gripper joint positions
        self.dq = -np.ones(16)*0.64
        self.dq[[1, 5, 9, 15]] = 0
        self.dq[12] = -0.7
        self.dq[13] = -0.7
        self.dq[14] = 2.443

        self.pos = init_pos  # (x, y, z)
        self.last_pos = np.zeros(3)
        self.grasp = False
        self.shift_on = False

    def start_control(self, init_pos=np.zeros(3)):
        """
        Method that should be called externally before controller can
        start receiving commands.
        """
        self._reset_internal_state(init_pos)
        self._reset_state = 0
        self._enabled = True

    def get_controller_state(self):
        """
        Grabs the current state of the keyboard.

        Returns:
            dict: A dictionary containing dpos, orn, unmodified orn, grasp, and reset
        """

        dpos = self.pos - self.last_pos
        self.last_pos = np.array(self.pos)
        raw_drotation = (
            self.raw_drotation - self.last_drotation
        )  # create local variable to return, then reset internal drotation
        self.last_drotation = np.array(self.raw_drotation)

        dq_clipped = copy.copy(self.dq)
        dq_clipped[12] = min(0.7, dq_clipped[12])
        # dq_clipped[14] = max(-0.8, dq_clipped[14])
        return dict(
            dpos=dpos,
            rotation=self.rotation,
            raw_drotation=raw_drotation,
            grasp=int(self.grasp),
            dq = dq_clipped,
            reset=self._reset_state,
        )

    def on_press(self, window, key, scancode, action, mods):
        """
        Key handler for key presses.

        Args:
            window: [NOT USED]
            key (int): keycode corresponding to the key that was pressed
            scancode: [NOT USED]
            action: [NOT USED]
            mods: [NOT USED]
        """

        # controls for moving position
        if key == glfw.KEY_W:
            self.pos[0] += self._pos_step * self.pos_sensitivity  # dec x
        elif key == glfw.KEY_S:
            self.pos[0] -= self._pos_step * self.pos_sensitivity  # inc x
        elif key == glfw.KEY_A:
            self.pos[1] += self._pos_step * self.pos_sensitivity  # dec y
        elif key == glfw.KEY_D:
            self.pos[1] -= self._pos_step * self.pos_sensitivity  # inc y
        elif key == glfw.KEY_F:
            self.pos[2] -= self._pos_step * self.pos_sensitivity  # dec z
        elif key == glfw.KEY_R:
            self.pos[2] += self._pos_step * self.pos_sensitivity  # inc z

        # controls for moving orientation
        elif key == glfw.KEY_Z:
            drot = rotation_matrix(angle=0.1 * self.rot_sensitivity, direction=[1.0, 0.0, 0.0])[:3, :3]
            self.rotation = self.rotation.dot(drot)  # rotates x
            self.raw_drotation[1] -= 0.1 * self.rot_sensitivity
        elif key == glfw.KEY_X:
            drot = rotation_matrix(angle=-0.1 * self.rot_sensitivity, direction=[1.0, 0.0, 0.0])[:3, :3]
            self.rotation = self.rotation.dot(drot)  # rotates x
            self.raw_drotation[1] += 0.1 * self.rot_sensitivity
        elif key == glfw.KEY_T:
            drot = rotation_matrix(angle=0.1 * self.rot_sensitivity, direction=[0.0, 1.0, 0.0])[:3, :3]
            self.rotation = self.rotation.dot(drot)  # rotates y
            self.raw_drotation[0] += 0.1 * self.rot_sensitivity
        elif key == glfw.KEY_G:
            drot = rotation_matrix(angle=-0.1 * self.rot_sensitivity, direction=[0.0, 1.0, 0.0])[:3, :3]
            self.rotation = self.rotation.dot(drot)  # rotates y
            self.raw_drotation[0] -= 0.1 * self.rot_sensitivity
        elif key == glfw.KEY_C:
            drot = rotation_matrix(angle=0.1 * self.rot_sensitivity, direction=[0.0, 0.0, 1.0])[:3, :3]
            self.rotation = self.rotation.dot(drot)  # rotates z
            self.raw_drotation[2] += 0.1 * self.rot_sensitivity
        elif key == glfw.KEY_V:
            drot = rotation_matrix(angle=-0.1 * self.rot_sensitivity, direction=[0.0, 0.0, 1.0])[:3, :3]
            self.rotation = self.rotation.dot(drot)  # rotates z
            self.raw_drotation[2] -= 0.1 * self.rot_sensitivity
        elif key == glfw.KEY_3 and self.shift_on:
            self.dq[key - glfw.KEY_1] += 0.01 * self.rot_sensitivity
            self.dq[key - glfw.KEY_1 + 2] -= 0.01 * self.rot_sensitivity
        elif key == glfw.KEY_3:
            self.dq[key - glfw.KEY_1] -= 0.01 * self.rot_sensitivity
            self.dq[key - glfw.KEY_1 + 2] += 0.01 * self.rot_sensitivity
        elif key == glfw.KEY_4 and self.shift_on:
            self.dq[key - glfw.KEY_1] += 0.01 * self.rot_sensitivity
            self.dq[key - glfw.KEY_1 + 2] -= 0.01 * self.rot_sensitivity
        elif key == glfw.KEY_4:
            self.dq[key - glfw.KEY_1] -= 0.01 * self.rot_sensitivity
            self.dq[key - glfw.KEY_1 + 2] += 0.01 * self.rot_sensitivity
        elif key <= glfw.KEY_9 and key >= glfw.KEY_1 and self.shift_on:
            self.dq[key-glfw.KEY_1] += 0.01*self.rot_sensitivity
        elif key <= glfw.KEY_9 and key >= glfw.KEY_1:
            self.dq[key-glfw.KEY_1] -= 0.01*self.rot_sensitivity

        if key == glfw.KEY_LEFT_SHIFT or key == glfw.KEY_RIGHT_SHIFT:
            self.shift_on = True

        if key == glfw.KEY_K:
            if self.dq[0] <= 1.5:
                self.dq[0] += self.alpha * self.pos_sensitivity
                self.dq[1] += self.alpha2 * self.pos_sensitivity
                self.dq[2] += self.alpha * self.pos_sensitivity
                self.dq[3] += self.alpha2 * self.pos_sensitivity
                self.dq[4] += self.alpha * self.pos_sensitivity
                self.dq[5] += self.alpha * self.pos_sensitivity
                self.dq[6] += self.alpha2 * self.pos_sensitivity

        if key == glfw.KEY_L:
            if self.dq[0] >= -1.5:
                self.dq[0] -= self.alpha * self.pos_sensitivity
                self.dq[1] -= self.alpha2 * self.pos_sensitivity
                self.dq[2] -= self.alpha * self.pos_sensitivity
                self.dq[3] -= self.alpha2 * self.pos_sensitivity
                self.dq[4] -= self.alpha * self.pos_sensitivity
                self.dq[5] -= self.alpha * self.pos_sensitivity
                self.dq[6] -= self.alpha2 * self.pos_sensitivity

        if key == glfw.KEY_I:
            if self.dq[0] <= 1.5:
                self.dq[0] += self.alpha * self.pos_sensitivity
                self.dq[2] += self.alpha * self.pos_sensitivity
                self.dq[3] += self.alpha * self.pos_sensitivity
                self.dq[4] += self.alpha * self.pos_sensitivity
                self.dq[6] += self.alpha * self.pos_sensitivity
                self.dq[7] += self.alpha * self.pos_sensitivity
                self.dq[8] += self.alpha * self.pos_sensitivity
                self.dq[10] += self.alpha * self.pos_sensitivity
                self.dq[11] += self.alpha * self.pos_sensitivity
                self.dq[12] += 2 * self.alpha * self.pos_sensitivity
                # self.dq[14] -= 3.5 *self.alpha * self.pos_sensitivity
                self.dq[14] = 2.443
                self.dq[15] += 0.5*self.alpha * self.pos_sensitivity


        if key == glfw.KEY_O:
            if self.dq[0] >= -1:
                self.dq[0] -= self.alpha * self.pos_sensitivity
                self.dq[2] -= self.alpha * self.pos_sensitivity
                self.dq[3] -= self.alpha * self.pos_sensitivity
                self.dq[4] -= self.alpha * self.pos_sensitivity
                self.dq[6] -= self.alpha * self.pos_sensitivity
                self.dq[7] -= self.alpha * self.pos_sensitivity
                self.dq[8] -= self.alpha * self.pos_sensitivity
                self.dq[10] -= self.alpha * self.pos_sensitivity
                self.dq[11] -= self.alpha * self.pos_sensitivity
                self.dq[12] -= 2 * self.alpha * self.pos_sensitivity
                # self.dq[14] += 3.5 *self.alpha * self.pos_sensitivity
                self.dq[14] = 2.443
                self.dq[15] -= 0.5 *self.alpha * self.pos_sensitivity



    def on_release(self, window, key, scancode, action, mods):
        """
        Key handler for key releases.

        Args:
            window: [NOT USED]
            key (int): keycode corresponding to the key that was pressed
            scancode: [NOT USED]
            action: [NOT USED]
            mods: [NOT USED]
        """

        # controls for grasping
        if key == glfw.KEY_SPACE:
            self.grasp = not self.grasp  # toggle gripper

        # user-commanded reset
        elif key == glfw.KEY_Q:
            self._reset_state = 1
            self._enabled = False
            self._reset_internal_state(np.zeros(3))

        elif key == glfw.KEY_LEFT_SHIFT or key == glfw.KEY_RIGHT_SHIFT:
            self.shift_on = False

    def on_pressed(self, window, key, scancode, action, mods):
        """
        Key handler for key releases.

        Args:
            window: [NOT USED]
            key (int): keycode corresponding to the key that was pressed
            scancode: [NOT USED]
            action: [NOT USED]
            mods: [NOT USED]
        """

        # controls for grasping
        if key == glfw.KEY_LEFT_SHIFT or key == glfw.KEY_RIGHT_SHIFT:
            self.shift_on = True
