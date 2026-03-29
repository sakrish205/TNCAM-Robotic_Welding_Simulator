import sim
import time


class CameraFollower:
    def __init__(self, clientID, camera_name="Camera", target_name="Target"):
        self.clientID = clientID
        self.camera_name = camera_name
        self.target_name = target_name
        self.camera_handle = -1
        self.target_handle = -1
        self.enabled = False
        self.offset = [0.5, -1.0, 0.8]

    def initialize(self):
        ret1, self.camera_handle = sim.simxGetObjectHandle(
            self.clientID, self.camera_name, sim.simx_opmode_blocking
        )
        ret2, self.target_handle = sim.simxGetObjectHandle(
            self.clientID, self.target_name, sim.simx_opmode_blocking
        )

        if ret1 == sim.simx_return_ok and ret2 == sim.simx_return_ok:
            return True
        return False

    def set_enabled(self, enabled):
        self.enabled = enabled

    def is_enabled(self):
        return self.enabled

    def set_offset(self, x, y, z):
        self.offset = [x, y, z]

    def update(self):
        if not self.enabled:
            return

        ret, target_pos = sim.simxGetObjectPosition(
            self.clientID, self.target_handle, -1, sim.simx_opmode_buffer
        )

        if ret == sim.simx_return_ok and target_pos:
            camera_pos = [
                target_pos[0] + self.offset[0],
                target_pos[1] + self.offset[1],
                target_pos[2] + self.offset[2],
            ]

            sim.simxSetObjectPosition(
                self.clientID,
                self.camera_handle,
                -1,
                camera_pos,
                sim.simx_opmode_oneshot,
            )

            ret, target_ori = sim.simxGetObjectOrientation(
                self.clientID, self.target_handle, -1, sim.simx_opmode_buffer
            )

            if ret == sim.simx_return_ok:
                sim.simxSetObjectOrientation(
                    self.clientID,
                    self.camera_handle,
                    -1,
                    target_ori,
                    sim.simx_opmode_oneshot,
                )

    def look_at_target(self):
        if self.target_handle == -1:
            return

        ret, target_pos = sim.simxGetObjectPosition(
            self.clientID, self.target_handle, -1, sim.simx_opmode_buffer
        )

        if ret == sim.simx_return_ok:
            sim.simxSetObjectPosition(
                self.clientID,
                self.camera_handle,
                -1,
                target_pos,
                sim.simx_opmode_oneshot,
            )


def create_camera_follower(clientID, camera_name="Camera", target_name="Target"):
    follower = CameraFollower(clientID, camera_name, target_name)
    if follower.initialize():
        return follower
    return None
