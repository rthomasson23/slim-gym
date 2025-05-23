from collections import OrderedDict

import numpy as np
import time
from scipy.spatial.transform import Rotation as R
from robosuite.environments.manipulation.single_arm_env import SingleArmEnv
from robosuite.models.arenas import ClutteredCabinet
from robosuite.models.objects import BoxObject, CylinderObject
from robosuite.models.tasks import ManipulationTask
from robosuite.utils.mjcf_utils import CustomMaterial
from robosuite.utils.observables import Observable, sensor
from robosuite.utils.placement_samplers import UniformRandomSampler
from robosuite.utils.transform_utils import convert_quat


class SequentialPickTrain(SingleArmEnv):
    """
    This class corresponds to the lifting task for a single robot arm.

    Args:
        robots (str or list of str): Specification for specific robot arm(s) to be instantiated within this env
            (e.g: "Sawyer" would generate one arm; ["Panda", "Panda", "Sawyer"] would generate three robot arms)
            Note: Must be a single single-arm robot!

        env_configuration (str): Specifies how to position the robots within the environment (default is "default").
            For most single arm environments, this argument has no impact on the robot setup.

        controller_configs (str or list of dict): If set, contains relevant controller parameters for creating a
            custom controller. Else, uses the default controller for this specific task. Should either be single
            dict if same controller is to be used for all robots or else it should be a list of the same length as
            "robots" param

        gripper_types (str or list of str): type of gripper, used to instantiate
            gripper models from gripper factory. Default is "default", which is the default grippers(s) associated
            with the robot(s) the 'robots' specification. None removes the gripper, and any other (valid) model
            overrides the default gripper. Should either be single str if same gripper type is to be used for all
            robots or else it should be a list of the same length as "robots" param

        initialization_noise (dict or list of dict): Dict containing the initialization noise parameters.
            The expected keys and corresponding value types are specified below:

            :`'magnitude'`: The scale factor of uni-variate random noise applied to each of a robot's given initial
                joint positions. Setting this value to `None` or 0.0 results in no noise being applied.
                If "gaussian" type of noise is applied then this magnitude scales the standard deviation applied,
                If "uniform" type of noise is applied then this magnitude sets the bounds of the sampling range
            :`'type'`: Type of noise to apply. Can either specify "gaussian" or "uniform"

            Should either be single dict if same noise value is to be used for all robots or else it should be a
            list of the same length as "robots" param

            :Note: Specifying "default" will automatically use the default noise settings.
                Specifying None will automatically create the required dict with "magnitude" set to 0.0.

        table_full_size (3-tuple): x, y, and z dimensions of the table.

        table_friction (3-tuple): the three mujoco friction parameters for
            the table.

        use_camera_obs (bool): if True, every observation includes rendered image(s)

        use_object_obs (bool): if True, include object (cube) information in
            the observation.

        reward_scale (None or float): Scales the normalized reward function by the amount specified.
            If None, environment reward remains unnormalized

        reward_shaping (bool): if True, use dense rewards.

        placement_initializer (ObjectPositionSampler): if provided, will
            be used to place objects on every reset, else a UniformRandomSampler
            is used by default.

        has_renderer (bool): If true, render the simulation state in
            a viewer instead of headless mode.

        has_offscreen_renderer (bool): True if using off-screen rendering

        render_camera (str): Name of camera to render if `has_renderer` is True. Setting this value to 'None'
            will result in the default angle being applied, which is useful as it can be dragged / panned by
            the user using the mouse

        render_collision_mesh (bool): True if rendering collision meshes in camera. False otherwise.

        render_visual_mesh (bool): True if rendering visual meshes in camera. False otherwise.

        render_gpu_device_id (int): corresponds to the GPU device id to use for offscreen rendering.
            Defaults to -1, in which case the device will be inferred from environment variables
            (GPUS or CUDA_VISIBLE_DEVICES).

        control_freq (float): how many control signals to receive in every second. This sets the amount of
            simulation time that passes between every action input.

        horizon (int): Every episode lasts for exactly @horizon timesteps.

        ignore_done (bool): True if never terminating the environment (ignore @horizon).

        hard_reset (bool): If True, re-loads model, sim, and render object upon a reset call, else,
            only calls sim.reset and resets all robosuite-internal variables

        camera_names (str or list of str): name of camera to be rendered. Should either be single str if
            same name is to be used for all cameras' rendering or else it should be a list of cameras to render.

            :Note: At least one camera must be specified if @use_camera_obs is True.

            :Note: To render all robots' cameras of a certain type (e.g.: "robotview" or "eye_in_hand"), use the
                convention "all-{name}" (e.g.: "all-robotview") to automatically render all camera images from each
                robot's camera list).

        camera_heights (int or list of int): height of camera frame. Should either be single int if
            same height is to be used for all cameras' frames or else it should be a list of the same length as
            "camera names" param.

        camera_widths (int or list of int): width of camera frame. Should either be single int if
            same width is to be used for all cameras' frames or else it should be a list of the same length as
            "camera names" param.

        camera_depths (bool or list of bool): True if rendering RGB-D, and RGB otherwise. Should either be single
            bool if same depth setting is to be used for all cameras or else it should be a list of the same length as
            "camera names" param.

        camera_segmentations (None or str or list of str or list of list of str): Camera segmentation(s) to use
            for each camera. Valid options are:

                `None`: no segmentation sensor used
                `'instance'`: segmentation at the class-instance level
                `'class'`: segmentation at the class level
                `'element'`: segmentation at the per-geom level

            If not None, multiple types of segmentations can be specified. A [list of str / str or None] specifies
            [multiple / a single] segmentation(s) to use for all cameras. A list of list of str specifies per-camera
            segmentation setting(s) to use.

    Raises:
        AssertionError: [Invalid number of robots specified]
    """

    def __init__(
        self,
        robots,
        env_configuration="default",
        controller_configs=None,
        gripper_types="default",
        initialization_noise="default",
        table_full_size=(0.38, 0.66, 0.07),
        table_friction=(0.2, 0.5, 0.1),
        use_camera_obs=True,
        use_object_obs=True,
        reward_scale=1.0,
        reward_shaping=False,
        placement_initializer=None,
        has_renderer=False,
        has_offscreen_renderer=True,
        render_camera="frontview",
        render_collision_mesh=False,
        render_visual_mesh=True,
        render_gpu_device_id=-1,
        control_freq=20,
        horizon=1000,
        ignore_done=False,
        hard_reset=True,
        camera_names="sideview",
        camera_heights=256,
        camera_widths=256,
        camera_depths=False,
        camera_segmentations=None,  # {None, instance, class, element}
        renderer="mujoco",
        renderer_config=None,
        initial_placement=None,
    ):
        # settings for table top
        self.table_full_size = table_full_size
        self.table_friction = table_friction
        self.table_offset = np.array((0.35, 0, 1.5))

        # reward configuration
        self.reward_scale = reward_scale
        self.reward_shaping = reward_shaping

        # whether to use ground-truth object states
        self.use_object_obs = use_object_obs

        # object placement initializer
        self.placement_initializer = placement_initializer
        self.placement_initializer2 = None

        # set up trial counter
        self.trial_counter = -1

        # define the goal position for the objects
        self.goal_zone_location = np.array([[0.035, 0.085],[-0.045, 0.045]])

        super().__init__(
            robots=robots,
            env_configuration=env_configuration,
            controller_configs=controller_configs,
            mount_types="default",
            gripper_types=gripper_types,
            initialization_noise=initialization_noise,
            use_camera_obs=use_camera_obs,
            has_renderer=has_renderer,
            has_offscreen_renderer=has_offscreen_renderer,
            render_camera=render_camera,
            render_collision_mesh=render_collision_mesh,
            render_visual_mesh=render_visual_mesh,
            render_gpu_device_id=render_gpu_device_id,
            control_freq=control_freq,
            horizon=horizon,
            ignore_done=ignore_done,
            hard_reset=hard_reset,
            camera_names=camera_names,
            camera_heights=camera_heights,
            camera_widths=camera_widths,
            camera_depths=camera_depths,
            camera_segmentations=camera_segmentations,
            renderer=renderer,
            renderer_config=renderer_config,
        )

    def reward(self, action=None):
        """
        Reward function for the task.

        Sparse un-normalized reward:

            - a discrete reward of 2.25 is provided if the cube is lifted

        Un-normalized summed components if using reward shaping:

            - Reaching: in [0, 1], to encourage the arm to reach the cube
            - Grasping: in {0, 0.25}, non-zero if arm is grasping the cube
            - Lifting: in {0, 1}, non-zero if arm has lifted the cube

        The sparse reward only consists of the lifting component.

        Note that the final reward is normalized and scaled by
        reward_scale / 2.25 as well so that the max score is equal to reward_scale

        Args:
            action (np array): [NOT USED]

        Returns:
            float: reward value
        """
        reward = 0.0


        return reward

    def _load_model(self):
        """
        Loads an xml model, puts it in self.model
        """
        super()._load_model()

        # Adjust base pose accordingly
        xpos = self.robots[0].robot_model.base_xpos_offset["table"](self.table_full_size[0])
        self.robots[0].robot_model.set_base_xpos(xpos)

        # load model for table top workspace
        # mujoco_arena = TableArena(
        #     table_full_size=self.table_full_size,
        #     table_friction=self.table_friction,
        #     table_offset=self.table_offset,
        # )
        mujoco_arena = ClutteredCabinet(
            table_full_size=self.table_full_size,
            table_friction=self.table_friction,
            table_offset=self.table_offset
        )

        # Arena always gets set to zero origin
        mujoco_arena.set_origin([0, 0, 0])

        # initialize objects of interest
        tex_attrib = {
            "type": "cube",
        }
        mat_attrib = {
            "texrepeat": "1 1",
            "specular": "0.4",
            "shininess": "0.1",
        }
        redwood = CustomMaterial(
            texture="WoodRed",
            tex_name="redwood",
            mat_name="redwood_mat",
            tex_attrib=tex_attrib,
            mat_attrib=mat_attrib,
        )

        greenwood = CustomMaterial(
            texture="WoodGreen",
            tex_name="greenwood",
            mat_name="greenwood_mat",
            tex_attrib=tex_attrib,
            mat_attrib=mat_attrib,
        )


        self.goal_object_1 = [CylinderObject(
            name=f"goal_object_1",
            size=[0.038, 0.112],
            rgba=[0.2, 1, 0.5, 1],
            material=greenwood,
            density=250,
        )]

        self.goal_object_2 = [CylinderObject(
            name=f"goal_object_2",
            size=[0.038, 0.112],
            rgba=[0.2, 1, 0.5, 1],
            material=greenwood,
            density=250,
        )]

       
        # Create placement initializer
        self.placement_initializer_1 = UniformRandomSampler(
            name="ObjectSampler",
            mujoco_objects=self.goal_object_1,
            x_range=[0.024, 0.034],
            y_range=[-0.24, -0.1],
            ensure_object_boundary_in_range=False,
            ensure_valid_placement=True,
            reference_pos=self.table_offset,
            rotation_axis='z',
            rotation=[0],
            z_offset=0.01,
        )

        self.placement_initializer_2 = UniformRandomSampler(
            name="ObjectSampler",
            mujoco_objects=self.goal_object_2,
            x_range=[0.024, 0.034],
            y_range=[0.1, 0.24],
            ensure_object_boundary_in_range=False,
            ensure_valid_placement=True,
            reference_pos=self.table_offset,
            rotation_axis='z',
            rotation=[0],
            z_offset=0.01,
        )


        # task includes arena, robot, and objects of interest
        self.model = ManipulationTask(
            mujoco_arena=mujoco_arena,
            mujoco_robots=[robot.robot_model for robot in self.robots],
            mujoco_objects=self.goal_object_1 + self.goal_object_2,
        )

    def _setup_references(self):
        """
        Sets up references to important components. A reference is typically an
        index or a list of indices that point to the corresponding elements
        in a flatten array, which is how MuJoCo stores physical simulation data.
        """
        super()._setup_references()

        # Additional object references from this env
        self.goal_object_1_body_id = self.sim.model.body_name2id(self.goal_object_1[0].root_body)
        self.goal_object_2_body_id = self.sim.model.body_name2id(self.goal_object_2[0].root_body)


    def _setup_observables(self):
        """
        Sets up observables to be used for this environment. Creates object-based observables if enabled

        Returns:
            OrderedDict: Dictionary mapping observable names to its corresponding Observable object
        """
        observables = super()._setup_observables()

        return observables

    def _reset_internal(self):
        """
        Resets simulation internal configurations.
        """
        super()._reset_internal()

        # start a timer to see how long it takes to succeed at the task
        self.start_time = time.time()

        # Reset all object positions using initializer sampler if we're not directly loading from an xml
        if not self.deterministic_reset:

            # set random seed
            np.random.seed(self.trial_counter + 2)
            self.trial_counter += 1

            if self.trial_counter > 2:
                exit()

            # Sample from the placement initializer for all objects
            object_placements_1 = self.placement_initializer_1.sample()
            object_placements_2 = self.placement_initializer_2.sample()

            count = 0
            # Loop through all objects and reset their positions
            for obj_pos, obj_quat, obj in object_placements_1.values():
                count += 1
                self.sim.data.set_joint_qpos(obj.joints[0], np.concatenate([np.array(obj_pos), np.array(obj_quat)]))

            for obj_pos, obj_quat, obj in object_placements_2.values():
                self.sim.data.set_joint_qpos(obj.joints[0], np.concatenate([np.array(obj_pos), np.array(obj_quat)]))
                

    def visualize(self, vis_settings):
        """
        In addition to super call, visualize gripper site proportional to the distance to the cube.

        Args:
            vis_settings (dict): Visualization keywords mapped to T/F, determining whether that specific
                component should be visualized. Should have "grippers" keyword as well as any other relevant
                options specified.
        """
        # Run superclass method first
        # super().visualize(vis_settings={vis: False for vis in self._visualizations})
        super().visualize(vis_settings={vis: True for vis in self._visualizations})

    def _check_success(self):
        """
        Check if object has been removed from the cabinet.

        Returns:
            bool: True if object has beenr removed. 
        """
        # get goal object positions
        goal_object_1_pos = self.sim.data.body_xpos[self.goal_object_1_body_id]
        goal_object_2_pos = self.sim.data.body_xpos[self.goal_object_2_body_id]

        # get goal object orientations
        goal_object_1_quat = self.sim.data.body_xquat[self.goal_object_1_body_id]
        goal_object_2_quat = self.sim.data.body_xquat[self.goal_object_2_body_id]

        # convert quaternions to euler angles
        rot_1 = R.from_quat(goal_object_1_quat)
        goal_object_1_euler = R.as_euler(rot_1, 'xyz')
        goal_object_1_y_axis = goal_object_1_euler[1]
        upright_bool_1 = np.abs(goal_object_1_y_axis) < 2e-4

        rot_2 = R.from_quat(goal_object_2_quat)
        goal_object_2_euler = R.as_euler(rot_2, 'xyz')
        goal_object_2_y_axis = goal_object_2_euler[1]
        upright_bool_2 = np.abs(goal_object_2_y_axis) < 2e-4

        # save object positions
        self.goal_object_1_pos = goal_object_1_pos
        self.goal_object_2_pos = goal_object_2_pos

        # check if object is in the goal zone
        goal_zone_bool_1 = (0.4 < goal_object_1_pos[0] < 0.46) and (-0.11 < goal_object_1_pos[1] < 0.11)
        goal_zone_bool_2 = (0.4 < goal_object_2_pos[0] < 0.46) and (-0.11 < goal_object_2_pos[1] < 0.11)

        # calculate success metrics
        object_1_placed = goal_zone_bool_1 and upright_bool_1
        object_2_placed = goal_zone_bool_2 and upright_bool_2

        # check if object is dropped
        dropped_bool_1 = goal_object_1_pos[2] < 0.5
        dropped_bool_2 = goal_object_2_pos[2] < 0.5

        elapsed_time = time.time() - self.start_time

        if object_1_placed and object_2_placed:
            return True, True, True, True, False
        elif (elapsed_time > 180) or dropped_bool_1 or dropped_bool_2:
            return True, False, False, False, True
        elif object_1_placed and not object_2_placed:
            return False, False, True, False, False
        elif object_2_placed and not object_1_placed:
            return False, False, False, True, False
        
        return False, False, False, False, False
    
    def _calculate_disturbance(self):
        pass
        # disturbance = 0
        # fall_penalty = 0.5
        # num_fallen_objects = 0
        # for i in range(len(self.objects)):
        #     pos = self.sim.data.body_xpos[self.obstacle_ids[i]]
        #     if pos[2] < 0.5: # if object is on the ground, penalize that
        #         disturbance += fall_penalty
        #         num_fallen_objects += 1
        #     else:
        #         initial_pos = self.initial_obstacle_positions[:,i]
        #         disturbance += np.linalg.norm(pos - initial_pos)
        # return disturbance, num_fallen_objects