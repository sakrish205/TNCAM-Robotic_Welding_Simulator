import sim
import time
import numpy as np


class SafetyController:
    def __init__(self, clientID, robot_name="Robot", human_name="Human"):
        self.clientID = clientID
        self.robot_name = robot_name
        self.human_name = human_name

        self.robot_handle = -1
        self.human_handle = -1

        self.red_zone_distance = 0.5
        self.yellow_zone_distance = 1.0

        self.current_state = "NORMAL"
        self.last_distance = float("inf")

        self.collision_handles = {}
        self.collision_enabled = True

    def initialize(self):
        ret1, self.robot_handle = sim.simxGetObjectHandle(
            self.clientID, self.robot_name, sim.simx_opmode_blocking
        )
        ret2, self.human_handle = sim.simxGetObjectHandle(
            self.clientID, self.human_name, sim.simx_opmode_blocking
        )

        collision_pairs = [
            "robot_cube_collision",
            "robot_table_collision",
            "robot_human_collision",
        ]

        for collision_name in collision_pairs:
            ret, handle = sim.simxGetCollisionHandle(
                self.clientID, collision_name, sim.simx_opmode_blocking
            )
            if ret == sim.simx_return_ok:
                self.collision_handles[collision_name] = handle
                print(f"Found collision object: {collision_name}")

        if ret1 == sim.simx_return_ok and ret2 == sim.simx_return_ok:
            return True
        return False

    def set_zones(self, red_distance=0.5, yellow_distance=1.0):
        self.red_zone_distance = red_distance
        self.yellow_zone_distance = yellow_distance

    def get_distance(self):
        if self.robot_handle == -1 or self.human_handle == -1:
            return float("inf")

        ret1, robot_pos = sim.simxGetObjectPosition(
            self.clientID, self.robot_handle, -1, sim.simx_opmode_buffer
        )
        ret2, human_pos = sim.simxGetObjectPosition(
            self.clientID, self.human_handle, -1, sim.simx_opmode_buffer
        )

        if ret1 == sim.simx_return_ok and ret2 == sim.simx_return_ok:
            distance = np.linalg.norm(np.array(robot_pos) - np.array(human_pos))
            self.last_distance = distance
            return distance

        return float("inf")

    def check_safety(self):
        distance = self.get_distance()

        if distance <= self.red_zone_distance:
            self.current_state = "STOP"
        elif distance <= self.yellow_zone_distance:
            self.current_state = "SLOW"
        else:
            self.current_state = "NORMAL"

        return self.current_state, distance

    def check_collision(self):
        if not self.collision_enabled:
            return False, None

        for collision_name, handle in self.collision_handles.items():
            ret, state = sim.simxReadCollision(
                self.clientID, handle, sim.simx_opmode_buffer
            )
            if ret == sim.simx_return_ok and state:
                return True, collision_name

        return False, None

    def check_all_collisions(self):
        collision_states = {}
        for collision_name, handle in self.collision_handles.items():
            ret, state = sim.simxReadCollision(
                self.clientID, handle, sim.simx_opmode_buffer
            )
            collision_states[collision_name] = (
                state if ret == sim.simx_return_ok else False
            )
        return collision_states

    def enable_collisions(self):
        self.collision_enabled = True

    def disable_collisions(self):
        self.collision_enabled = False

    def get_status(self):
        collision_state, collision_name = self.check_collision()
        return {
            "state": self.current_state,
            "distance": self.last_distance,
            "red_zone": self.red_zone_distance,
            "yellow_zone": self.yellow_zone_distance,
            "collision_detected": collision_state,
            "collision_object": collision_name,
        }

    def is_safe_to_move(self):
        state, _ = self.check_safety()
        collision, _ = self.check_collision()
        return state != "STOP" and not collision

    def get_recommended_speed(self):
        state, distance = self.check_safety()
        collision, _ = self.check_collision()

        if collision or state == "STOP":
            return 0.0
        elif state == "SLOW":
            return 0.3
        else:
            return 1.0

    def visualize_zones(self, base_position=None):
        if base_position is None:
            if self.robot_handle != -1:
                ret, base_position = sim.simxGetObjectPosition(
                    self.clientID, self.robot_handle, -1, sim.simx_opmode_buffer
                )
                if ret != sim.simx_return_ok:
                    base_position = [0, 0, 0]
            else:
                base_position = [0, 0, 0]

        return {
            "red_center": base_position,
            "red_radius": self.red_zone_distance,
            "yellow_center": base_position,
            "yellow_radius": self.yellow_zone_distance,
        }


def create_safety_controller(clientID, robot_name="Robot", human_name="Human"):
    controller = SafetyController(clientID, robot_name, human_name)
    if controller.initialize():
        return controller
    return None
