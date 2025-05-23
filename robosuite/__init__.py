from robosuite.environments.base import make

# Manipulation environments
from robosuite.environments.manipulation.lift import Lift
from robosuite.environments.manipulation.constrained_reorient import ConstrainedReorient
from robosuite.environments.manipulation.drawer_pick import DrawerPick
from robosuite.environments.manipulation.train import Train
from robosuite.environments.manipulation.bookshelf import Bookshelf
from robosuite.environments.manipulation.reach import Reach
from robosuite.environments.manipulation.stack import Stack
from robosuite.environments.manipulation.nut_assembly import NutAssembly
from robosuite.environments.manipulation.pick_place import PickPlace
from robosuite.environments.manipulation.door import Door
from robosuite.environments.manipulation.wipe import Wipe
from robosuite.environments.manipulation.two_arm_lift import TwoArmLift
from robosuite.environments.manipulation.two_arm_peg_in_hole import TwoArmPegInHole
from robosuite.environments.manipulation.two_arm_handover import TwoArmHandover
from robosuite.environments.manipulation.train_cabinet import TrainCabinet
from robosuite.environments.manipulation.drawer_pick_train import DrawerPickTrain
from robosuite.environments.manipulation.constrained_reorient_train import ConstrainedReorientTrain
from robosuite.environments.manipulation.bookshelf_train import BookshelfTrain
from robosuite.environments.manipulation.sequential_pick import SequentialPick
from robosuite.environments.manipulation.sequential_pick_train import SequentialPickTrain

from robosuite.environments import ALL_ENVIRONMENTS
from robosuite.controllers import ALL_CONTROLLERS, load_controller_config
from robosuite.robots import ALL_ROBOTS
from robosuite.models.grippers import ALL_GRIPPERS

__version__ = "1.3.1"
__logo__ = """
      ;     /        ,--.
     ["]   ["]  ,<  |__**|
    /[_]\  [~]\/    |//  |
     ] [   OOO      /o|__|
"""
