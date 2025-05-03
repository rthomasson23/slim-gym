## Overview
This project uses [robosuite](https://github.com/ARISE-Initiative/robosuite), a modular simulation framework for robot learning developed by Zhu et al. (2020). We have modified robosuite to add new robot models (including the model for SLIM and our custom differential wrist), new tasks, and an Oculus Meta Quest teleoperation interface. The Meta Quest interfaces utilizes [oculus_reader](https://github.com/rail-berkeley/oculus_reader) by Jedrzej Orbik and Frederik Ebert (2021).

## Models
* See the following [python class for the SLIM hand](robosuite/models/grippers/sslim_hand.py) which points to the [MuJoCo XML for SLIM](robosuite/models/assets/grippers/sslim_hand_CH.xml)
* The following includes the [python class for the Franka arm appended with our supplemental wrist](https://github.com/rthomasson23/slim-gym/blob/master/robosuite/models/robots/manipulators/panda_sslim.py)

## Tasks
See the following files for the task environments. In each file, the `_check_success()` method encodes the definition of success and is used for automatic task completion detection. 
* The Cabinet Pick task is defined [here](https://github.com/rthomasson23/slim-gym/blob/master/robosuite/environments/manipulation/bookshelf.py).
* The Cabinet Reorient task is defined [here](https://github.com/rthomasson23/slim-gym/blob/master/robosuite/environments/manipulation/constrained_reorient.py).
* The Box Pick task is defined [here](https://github.com/rthomasson23/slim-gym/blob/master/robosuite/environments/manipulation/drawer_pick.py).
* The Cabinet Reorganize task is defined [here](https://github.com/rthomasson23/slim-gym/blob/master/robosuite/environments/manipulation/sequential_pick.py).

## Teleoperation Interface
The interface for the Oculus Meta Quest controller is found [here](https://github.com/rthomasson23/slim-gym/blob/master/robosuite/devices/oculus.py). This interfaces between robosuite and oculus_reader. 

## Operational Space Controller
Robosuite provides an operational space controller, which is used here for task-space teleoperation. The file implementing this controller is found [here](https://github.com/rthomasson23/slim-gym/blob/master/robosuite/controllers/osc.py).  

## Citations

@inproceedings{robosuite2020,
  title={robosuite: A Modular Simulation Framework and Benchmark for Robot Learning},
  author={Yuke Zhu and Josiah Wong and Ajay Mandlekar and Roberto Mart\'{i}n-Mart\'{i}n and Abhishek Joshi and Soroush Nasiriany and Yifeng Zhu and Kevin Lin},
  booktitle={arXiv preprint arXiv:2009.12293},
  year={2020}
}

@misc{OrbikEbert2021OculusReader,
  author = {Jedrzej Orbik and Frederik Ebert},
  title = {Oculus Reader: Robotic Teleoperation Interface},
  year = {2021},
  url = {https://github.com/rail-berkeley/oculus_reader},
  note = {Accessed: 2025-04-24}
}
