"""TNCAM - Robotic Welding Simulation
CoppeliaSim Edition

Migration from PyBullet to CoppeliaSim
Version: 1.0.0
Date: 2026-02-22
"""

import os
import sys

src_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(src_dir)

if project_root not in sys.path:
    sys.path.insert(0, project_root)

__version__ = "1.0.0"
__author__ = "TNCAM Team"

from . import coppelia_client
from . import moveRobot
from . import jointControl
from . import cameraFollow
from . import path_loader
from . import data_logger
from . import weldingTorch
from . import vision
from . import safety_controller
from . import human_obstacle
from . import workspace_layout
from . import endpoint_tracker
from . import ik_solver

__all__ = [
    "coppelia_client",
    "moveRobot",
    "jointControl",
    "cameraFollow",
    "path_loader",
    "data_logger",
    "weldingTorch",
    "vision",
    "safety_controller",
    "human_obstacle",
    "workspace_layout",
    "endpoint_tracker",
    "ik_solver",
    "get_asset_path",
    "get_data_path",
]


def get_asset_path(*paths):
    return os.path.join(project_root, "assets", *paths)


def get_data_path(*paths):
    return os.path.join(project_root, "data", *paths)
