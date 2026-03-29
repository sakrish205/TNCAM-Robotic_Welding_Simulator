import sim
import time
import numpy as np
import random


class HumanObstacle:
    def __init__(self, clientID, human_name="Human"):
        self.clientID = clientID
        self.human_name = human_name
        self.human_handle = -1

        self.default_position = [1.2, 0.0, 0.85]
        self.current_position = self.default_position.copy()

        self.move_speed = 0.5
        self.movement_enabled = False

        self.min_distance = 0.5
        self.max_distance = 2.0

    def initialize(self):
        ret, self.human_handle = sim.simxGetObjectHandle(
            self.clientID, self.human_name, sim.simx_opmode_blocking
        )

        if ret == sim.simx_return_ok:
            self.set_position(self.default_position)
            return True
        return False

    def set_position(self, position):
        if self.human_handle == -1:
            return False

        sim.simxSetObjectPosition(
            self.clientID, self.human_handle, -1, position, sim.simx_opmode_oneshot
        )
        self.current_position = position.copy()
        return True

    def get_position(self):
        if self.human_handle == -1:
            return self.default_position.copy()

        ret, position = sim.simxGetObjectPosition(
            self.clientID, self.human_handle, -1, sim.simx_opmode_buffer
        )

        if ret == sim.simx_return_ok:
            self.current_position = position
            return position

        return self.current_position.copy()

    def move_toward_robot(self, robot_position, speed=None):
        if speed is None:
            speed = self.move_speed

        current = np.array(self.get_position())
        target = np.array(robot_position)

        direction = target - current
        distance = np.linalg.norm(direction)

        if distance > self.min_distance:
            step = (direction / distance) * speed * 0.1
            new_position = current + step

            sim.simxSetObjectPosition(
                self.clientID,
                self.human_handle,
                -1,
                new_position.tolist(),
                sim.simx_opmode_oneshot,
            )
            self.current_position = new_position.tolist()

        return self.current_position

    def move_away_from_robot(self, robot_position, speed=None):
        if speed is None:
            speed = self.move_speed

        current = np.array(self.get_position())
        target = np.array(robot_position)

        direction = current - target
        distance = np.linalg.norm(direction)

        if distance < self.max_distance:
            step = (direction / distance) * speed * 0.1
            new_position = current + step

            sim.simxSetObjectPosition(
                self.clientID,
                self.human_handle,
                -1,
                new_position.tolist(),
                sim.simx_opmode_oneshot,
            )
            self.current_position = new_position.tolist()

        return self.current_position

    def move_random(self, bounds=None):
        if bounds is None:
            bounds = {
                "x_min": 0.5,
                "x_max": 2.0,
                "y_min": -1.0,
                "y_max": 1.0,
                "z": 0.85,
            }

        new_position = [
            random.uniform(bounds["x_min"], bounds["x_max"]),
            random.uniform(bounds["y_min"], bounds["y_max"]),
            bounds["z"],
        ]

        self.set_position(new_position)
        return new_position

    def set_speed(self, speed):
        self.move_speed = max(0.1, min(2.0, speed))

    def get_speed(self):
        return self.move_speed

    def reset_position(self):
        self.set_position(self.default_position)
        return self.default_position.copy()

    def get_distance_to_robot(self, robot_position):
        current = np.array(self.get_position())
        target = np.array(robot_position)
        return np.linalg.norm(target - current)


def create_human_obstacle(clientID, human_name="Human"):
    obstacle = HumanObstacle(clientID, human_name)
    if obstacle.initialize():
        return obstacle
    return None
