import sim
import time
import numpy as np
from .ik_solver import IKSolver
from . import moveRobot

JOINT_LIMITS = {
    1: (-np.pi, np.pi),
    2: (-np.pi / 2, np.pi / 2),
    3: (-np.pi / 2, np.pi / 2),
    4: (-2 * np.pi, 2 * np.pi),
    5: (-np.pi / 2, np.pi / 2),
    6: (-2 * np.pi, 2 * np.pi),
}

DEFAULT_TORCH_OFFSET = [0, 0, -0.01]
DEFAULT_ROBOT_BASE = [0, 0, 0.0975]


def detect_robot_name(clientID):
    common_names = ["IRB4600", "Robot", "Kuka", "UR5", "Arm", "arm"]
    for name in common_names:
        ret, handle = sim.simxGetObjectHandle(clientID, name, sim.simx_opmode_blocking)
        if ret == sim.simx_return_ok:
            return name
    return "IRB4600"


class JointController:
    def __init__(self, clientID, robot_name="IRB4600"):
        self.clientID = clientID
        self.robot_name = robot_name
        self.joint_handles = []
        self.joint_names = []
        self.current_positions = []
        self.target_handle = -1
        self.torch_offset = np.array(DEFAULT_TORCH_OFFSET)
        self.robot_base = np.array(DEFAULT_ROBOT_BASE)
        self.ik_solver = IKSolver()

    def initialize(self):
        self.joint_handles = []
        self.joint_names = []

        for i in range(1, 7):
            name = f"{self.robot_name}_joint{i}"
            ret, handle = sim.simxGetObjectHandle(
                self.clientID, name, sim.simx_opmode_blocking
            )
            if ret == sim.simx_return_ok:
                self.joint_handles.append(handle)
                self.joint_names.append(name)

                # Enable position control
                try:
                    sim.simxSetObjectIntParameter(
                        self.clientID, handle, 2001, 1, sim.simx_opmode_blocking
                    )
                except:
                    pass
            else:
                print(f"Warning: Could not find joint {name}")

        self._find_target_handle()
        self.refresh_positions()
        return len(self.joint_handles) > 0

    def _find_target_handle(self):
        target_names = ["Target", "target", "shape", "shape0", "shape1", "Tip", "tip"]
        for name in target_names:
            ret, handle = sim.simxGetObjectHandle(
                self.clientID, name, sim.simx_opmode_blocking
            )
            if ret == sim.simx_return_ok:
                self.target_handle = handle
                print(f"Found target object: {name}")
                return True
        print("Warning: No target object found for IK")
        return False

    def refresh_positions(self):
        self.current_positions = []
        for handle in self.joint_handles:
            ret, pos = sim.simxGetJointPosition(
                self.clientID, handle, sim.simx_opmode_buffer
            )
            if ret == sim.simx_return_ok:
                self.current_positions.append(pos)
            else:
                self.current_positions.append(0.0)
        return self.current_positions

    def set_joint(self, index, position, speed=1.0):
        if index < 0 or index >= len(self.joint_handles):
            return False

        limits = JOINT_LIMITS.get(index + 1, (-np.pi, np.pi))
        position = np.clip(position, limits[0], limits[1])

        sim.simxSetJointTargetPosition(
            self.clientID, self.joint_handles[index], position, sim.simx_opmode_oneshot
        )
        time.sleep(0.1 / max(speed * moveRobot.SPEED_FACTOR, 0.1))
        return True

    def set_all_joints(self, positions, speed=1.0):
        if len(positions) != len(self.joint_handles):
            return False

        for i, pos in enumerate(positions):
            self.set_joint(i, pos, speed)

        time.sleep(0.5 / max(speed * moveRobot.SPEED_FACTOR, 0.1))
        return True

    def get_joint(self, index):
        self.refresh_positions()
        if 0 <= index < len(self.current_positions):
            return self.current_positions[index]
        return None

    def get_all_joints(self):
        self.refresh_positions()
        return self.current_positions.copy()

    def get_current_joints_string(self):
        positions = self.get_all_joints()
        return ", ".join([f"J{i + 1}={p:.3f}" for i, p in enumerate(positions)])

    def go_home(self, speed=1.0):
        # Calibrated home position - torch ON cube surface
        home_positions = [-0.038863, 0.160718, 0.359108, 0.000310, -0.074666, 0.0]

        # Move using velocity control
        velocity = 0.5 * speed * moveRobot.SPEED_FACTOR

        self.refresh_positions()

        for i, target_pos in enumerate(home_positions):
            if i >= len(self.joint_handles):
                break

            diff = target_pos - self.current_positions[i]

            if abs(diff) > 0.001:
                direction = 1 if diff > 0 else -1
                move_time = abs(diff) / velocity

                sim.simxSetJointTargetVelocity(
                    self.clientID,
                    self.joint_handles[i],
                    direction * velocity,
                    sim.simx_opmode_oneshot,
                )

                time.sleep(move_time)

                sim.simxSetJointTargetVelocity(
                    self.clientID, self.joint_handles[i], 0, sim.simx_opmode_oneshot
                )

        return True

    def move_to_joint_positions(self, positions, speed=1.0):
        if len(positions) != len(self.joint_handles):
            print(
                f"Error: Expected {len(self.joint_handles)} positions, got {len(positions)}"
            )
            return False

        self.refresh_positions()
        start_positions = self.current_positions.copy()

        steps = 30
        for step in range(steps + 1):
            alpha = step / steps
            for i, target_pos in enumerate(positions):
                limits = JOINT_LIMITS.get(i + 1, (-np.pi, np.pi))
                start_pos = start_positions[i]
                interp_pos = start_pos + (target_pos - start_pos) * alpha
                clipped_pos = np.clip(interp_pos, limits[0], limits[1])

                sim.simxSetJointTargetPosition(
                    self.clientID,
                    self.joint_handles[i],
                    clipped_pos,
                    sim.simx_opmode_oneshot,
                )

            time.sleep(0.02 / max(speed * moveRobot.SPEED_FACTOR, 0.1))

        return True

    def move_joints_velocity(self, positions, speed=1.0, force=False):
        if len(positions) != len(self.joint_handles):
            print(
                f"Error: Expected {len(self.joint_handles)} positions, got {len(positions)}"
            )
            return False

        self.refresh_positions()

        velocity = 0.5 * speed * moveRobot.SPEED_FACTOR

        threshold = 0.0001 if force else 0.01

        for i, target_pos in enumerate(positions):
            diff = target_pos - self.current_positions[i]

            # Always move if force=True or diff is significant
            if force or abs(diff) > threshold:
                direction = 1 if diff > 0 else -1
                move_time = max(abs(diff) / velocity, 0.1)  # Minimum 0.1s

                # Set velocity to move
                ret = sim.simxSetJointTargetVelocity(
                    self.clientID,
                    self.joint_handles[i],
                    direction * velocity,
                    sim.simx_opmode_oneshot,
                )

                time.sleep(move_time)

                # Stop the joint
                sim.simxSetJointTargetVelocity(
                    self.clientID, self.joint_handles[i], 0, sim.simx_opmode_oneshot
                )

                time.sleep(0.05)

        return True

    def test_joint(self, joint_index, position, speed=0.3):
        if joint_index < 0 or joint_index >= len(self.joint_handles):
            print(f"Invalid joint index: {joint_index}")
            return False

        limits = JOINT_LIMITS.get(joint_index + 1, (-np.pi, np.pi))
        clamped_pos = np.clip(position, limits[0], limits[1])

        sim.simxSetJointTargetPosition(
            self.clientID,
            self.joint_handles[joint_index],
            clamped_pos,
            sim.simx_opmode_oneshot,
        )
        time.sleep(0.5 / max(speed * moveRobot.SPEED_FACTOR, 0.1))
        return True

    def move_to_pose(self, positions, speed=1.0):
        return self.move_joints_velocity(positions, speed)

    def move_to_world_position(self, x, y, z, speed=1.0):
        joint_angles = self.ik_solver.calculate_ik(x, y, z)
        return self.move_joints_velocity(joint_angles, speed)

    def move_to_ik_target(self, x, y, z, speed=1.0):
        joint_angles = self.ik_solver.calculate_ik(x, y, z)

        actual_pos = self.ik_solver.get_end_effector_position(joint_angles)
        error = (
            (actual_pos[0] - x) ** 2
            + (actual_pos[1] - y) ** 2
            + (actual_pos[2] - z) ** 2
        ) ** 0.5

        if error > 0.05:
            print(f"Warning: IK error {error * 1000:.1f}mm")

        # Move joints - use oneshot like Lua
        for i, pos in enumerate(joint_angles):
            if i < len(self.joint_handles):
                sim.simxSetJointTargetPosition(
                    self.clientID,
                    self.joint_handles[i],
                    pos,
                    sim.simx_opmode_oneshot,
                )

        return True

    def set_torch_offset(self, offset):
        if isinstance(offset, (list, tuple)):
            self.torch_offset = np.array(offset)
        else:
            self.torch_offset = np.array([0, 0, offset])

    def set_robot_base(self, base):
        if isinstance(base, (list, tuple)):
            self.robot_base = np.array(base)

    def get_ik_info(self):
        return {
            "robot_base": self.robot_base.tolist(),
            "torch_offset": self.torch_offset.tolist(),
            "target_handle": self.target_handle,
            "ik_solver": "Numerical IK (Newton-Raphson)",
        }

    def get_current_end_effector_position(self):
        self.refresh_positions()
        return self.ik_solver.get_end_effector_position(self.current_positions)


def create_joint_controller(clientID, robot_name="IRB4600"):
    controller = JointController(clientID, robot_name)
    if controller.initialize():
        return controller
    return None
